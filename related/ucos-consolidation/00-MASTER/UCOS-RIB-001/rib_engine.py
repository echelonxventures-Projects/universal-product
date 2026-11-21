#!/usr/bin/env python3
"""UCOS-RIB-001 — Repository Integration Blueprint engine.

AUTHORITY = NONE (DERIVED TRUTH). This engine legislates nothing, ratifies nothing,
freezes no architecture and owns no capability. It is the executable expression of
the chartered epic: it reads one DATA declaration (``rib-blueprint.json``) that declares how the
repository is to be DISCOVERED, how each discovered unit is to be MEASURED, which
matrices are already owned elsewhere and must be BOUND rather than restated, and by which
ordered, total rule set exactly one disposition is COMPUTED for every unit — then it
computes, never asserts, the inventory, the capability graph, the dependency planes, the
duplicate and gap registers, the queue, and the twelve gate verdicts.

    python3 00-MASTER/UCOS-RIB-001/rib_engine.py                      # regenerate + report
    python3 00-MASTER/UCOS-RIB-001/rib_engine.py --gate               # fail-closed
    python3 00-MASTER/UCOS-RIB-001/rib_engine.py --check-declaration
    python3 00-MASTER/UCOS-RIB-001/rib_engine.py --check-no-enumeration
    python3 00-MASTER/UCOS-RIB-001/rib_engine.py --check-write-scope
    python3 00-MASTER/UCOS-RIB-001/rib_engine.py --check-determinism
    python3 00-MASTER/UCOS-RIB-001/rib_engine.py --check-substrate
    python3 00-MASTER/UCOS-RIB-001/rib_engine.py --check-no-fabrication
    python3 00-MASTER/UCOS-RIB-001/rib_engine.py --check-reuse-before-create
    python3 00-MASTER/UCOS-RIB-001/rib_engine.py --check-totality

Exit semantics of --gate:
    0  every blocking gate passed
    1  a blocking gate failed
    2  fail-closed abort — the declaration or a required substrate is unusable, so no
       verdict may be asserted

The engine contains no unit identifier, no capability name, no disposition name, no
matrix/gate/output identifier and no substrate path as a literal; the blueprint is DATA
and a self-check proves it. Adding a discovery source, a measure, a plane, a disposition,
a rule, a matrix, a gap class, a duplicate class, a gate or an output is an edit to the
declaration and needs no code change.

Stdlib only. No network. No timestamp is emitted anywhere, so the rendered output set is
byte-identical for an unchanged repository state.
"""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
import re
import subprocess
import sys
import tomllib
from collections.abc import Callable
from pathlib import Path
from typing import Any, NoReturn

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
DECLARATION = HERE / "rib-blueprint.json"
EVIDENCE_DIR = HERE / "evidence"
EVIDENCE_INDEX = "rib-evidence-index.json"
MODEL_FILE = "rib.json"

# Keys an entry of each declared list-section may carry. A key outside its allowed set is
# a fail-closed violation: it prevents a new obligation, a hidden assumption or an unbound
# claim from being smuggled in through a new field. The section names are engine
# vocabulary; their contents are DATA.
ALLOWED_KEYS: dict[str, set[str]] = {
    "tracking": {"id", "family", "value", "allocation", "purpose"},
    "substrate": {"id", "path", "kind", "required", "generated", "pointers", "purpose"},
    "discovery": {
        "id",
        "kind",
        "class",
        "selector",
        "key_depth",
        "substrate",
        "pointer",
        "key_field",
        "location_field",
        "fields",
        "purpose",
    },
    "enrichment": {
        "id",
        "substrate",
        "pointer",
        "match_field",
        "match_mode",
        "fields",
        "purpose",
    },
    "measures": {
        "id",
        "kind",
        "selector_template",
        "selector_templates",
        "exclude_templates",
        "selector",
        "exclude",
        "substrate",
        "pointer",
        "record_field",
        "field",
        "match_leaf",
        "purpose",
    },
    "entrypoints": {"id", "selector", "purpose"},
    "reachability": {"id", "field", "purpose"},
    "planes": {
        "id",
        "kind",
        "unit_class",
        "exclude_typing_guard",
        "substrate",
        "pointer",
        "from_field",
        "to_field",
        "type_field",
        "dependency_types",
        "consumer_types",
        "provider_types",
        "implementation_types",
        "authority_types",
        "purpose",
    },
    "cycle_classes": {"id", "benign", "rule", "definition", "evidence"},
    "dispositions": {
        "id",
        "disposition",
        "definition",
        "requires_existing",
        "is_reuse",
        "is_change",
        "is_removal",
        "consumes_queue",
    },
    "disposition_rules": {"id", "disposition", "when", "because"},
    "matrices": {"id", "index", "name", "subject", "mode", "canonical_owner", "columns"},
    "gaps": {"id", "class", "subject", "field", "op", "value", "restrict_class"},
    "duplicates": {
        "id",
        "class",
        "blocking",
        "subject",
        "rule",
        "substrate",
        "pointer",
        "field",
        "value",
        "label_field",
        "scope_field",
        "scope_prefix",
        "exclude_prefix",
    },
    "verifications": {"id", "name", "criterion", "metric", "expect"},
    "validations": {"id", "name", "criterion", "metric", "expect"},
    # `basis` is inert documentation: it names the authority a gate rests on and, where one
    # exists, the measurement defect that shaped it. Nothing reads it and it is dropped from
    # the generated rib.json, so it carries no obligation and smuggles no claim — which is the
    # only thing this allow-list exists to prevent. GATE-12 records under it why the gate
    # measures the ignored-inclusive filesystem rather than `git status --porcelain`, a finding
    # that would be destroyed rather than declared if the key were simply removed.
    "gates": {"id", "name", "blocking", "criterion", "metrics", "basis", "working_tree_transitive"},
    "outputs": {"id", "file", "title", "purpose"},
    "severities": {"id", "severity", "rank", "definition"},
    "compliance": {"id", "requirement", "gate", "severity_on_fail", "remediation"},
    "references": {"id", "path", "purpose"},
    "non_derivable": {
        "id",
        "fact",
        "reason",
        "required_evidence_class",
        "bounds",
        "bounds_field",
        "owner",
        "probe",
    },
    "probes": {"id", "kind", "substrate", "pointer", "field", "value", "purpose"},
    "work_packages": {
        "id",
        "title",
        "owner",
        "route",
        "authorization_required",
        "discharges",
        "acceptance",
    },
}

# Programme fields that must name a located artefact. A reuse claim over an unresolvable
# reference is an empty claim.
PROGRAMME_REFERENCE_KEYS = (
    "governing_instrument",
    "operational_home",
    "operational_memory_owner",
    "registration_owner",
    "aggregate_gate_owner",
    "resilience_owner",
    "evolution_owner",
    "reality_owner",
    "capability_owner",
)

PROGRAMME_SCALAR_KEYS = (
    "id",
    "name",
    "version",
    "charter_designation",
    "mission",
    "prompt",
    "authority",
    "gate_name",
    "gate_clause",
    "determination_pass",
    "determination_fail",
    "disclosure",
)

# Reference strings may carry human suffixes. A reference resolves by exact path, then by
# glob, then by unique prefix within its parent directory.
_SUFFIX_SPLITS = (" (", " \u00a7", " Art ", " \u00b7 ", " \u2014 ")


# --------------------------------------------------------------------------- helpers


def fail_closed(message: str) -> NoReturn:
    print(f"FAIL-CLOSED ABORT — {message}", file=sys.stderr)
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


def git(*args: str, strip: bool = True) -> str:
    """Run git and return stdout.

    ``strip`` must be False for porcelain status: its records begin with a two-character
    status field that is often a leading space, and stripping the whole output silently
    shifts the first record by one character — turning a path into a different path.
    """
    try:
        out = subprocess.run(  # noqa: S603 — fixed argv, no shell, no user input
            ["git", *args],  # noqa: S607 — resolved from PATH by design, as CI does
            cwd=REPO,
            capture_output=True,
            text=True,
            check=False,
        )
        return out.stdout.strip() if strip else out.stdout
    except OSError:
        return ""


_SELECTOR_CACHE: dict[tuple[str, ...], list[str]] = {}
_TRACKED_SET: set[str] | None = None
_TRACKED_DIRS: set[str] | None = None


def tracked_universe() -> tuple[set[str], set[str]]:
    """The whole version-controlled path set, read once.

    Membership is answered from this set rather than by one subprocess per probe: the
    register alone would otherwise cost more than a thousand process spawns per run, and
    the determinism guard runs the whole model twice.
    """
    global _TRACKED_SET, _TRACKED_DIRS
    if _TRACKED_SET is None:
        files = {line for line in git("ls-files", "-z").split("\0") if line.strip()}
        dirs: set[str] = set()
        for rel in files:
            parts = rel.split("/")
            for index in range(1, len(parts)):
                dirs.add("/".join(parts[:index]))
        _TRACKED_SET, _TRACKED_DIRS = files, dirs
    return _TRACKED_SET, _TRACKED_DIRS


def tracked(*selectors: str) -> list[str]:
    """Version-controlled paths matching the declared pathspecs.

    ``-z`` is mandatory: without it git quotes any path containing a non-ASCII byte, and
    a quoted path is not the path — it would silently become a different unit key.
    Exclusion pathspecs must travel in the same invocation as the pathspec they narrow,
    so every selector for one measure is passed together rather than unioned afterwards.
    """
    args = tuple(item for item in selectors if item)
    if not args:
        return []
    cached = _SELECTOR_CACHE.get(args)
    if cached is None:
        out = git("ls-files", "-z", "--", *args)
        cached = [line for line in out.split("\0") if line.strip()]
        _SELECTOR_CACHE[args] = cached
    return cached


def is_tracked(path: str) -> bool:
    if not path:
        return False
    files, dirs = tracked_universe()
    return path in files or path in dirs


def repository_state() -> dict:
    porcelain = git("status", "--porcelain", strip=False)
    entries = [line for line in porcelain.splitlines() if line.strip()]
    conflicts = list(tracked_conflicts())
    git_dir = REPO / ".git"
    interrupted = sorted(
        child.name
        for child in (git_dir.iterdir() if git_dir.is_dir() else [])
        if re.match(r"^(MERGE_HEAD|CHERRY_PICK_HEAD|REVERT_HEAD|BISECT_LOG|rebase-)", child.name)
    )
    return {
        # UCOS-RFP-001 RFP-2 — the containing commit's identity is owned by version
        # control and is never restated in a tracked artifact: an artifact naming its
        # own commit demands a commit whose hash lies inside its own tree, so no
        # regeneration of it can converge. Detachment is retained because the
        # declared integrity gate consumes it, and observing it is not
        # self-referential: writing an artifact does not detach HEAD.
        "anchor": "the containing commit — owned by version control, never restated here",
        "detached": not git("symbolic-ref", "-q", "HEAD"),
        "working_tree": "DIRTY" if entries else "CLEAN",
        "raw_entries": entries,
        "conflicts": len(conflicts),
        "interrupted_operations": interrupted,
        "broken_symlinks": broken_symlinks(),
        "tracked_files": len(tracked(".")),
        # UCOS-CL-003 — object-database integrity. GATE-02 declares itself the Repository
        # Integrity gate and reported PASS against a demonstrably corrupt database: ten
        # Finder-duplicated artifacts sat inside .git, one of them a malformed ref
        # (`refs/heads/integration/recovery-001 2`) that made `git fsck` report badRefName
        # and `git log --all`, `--branches` and `rev-list --all` all exit 128. Nothing in
        # the programme looked, because integrity was measured only over the WORKING TREE.
        # .gitignore cannot reach .git, so no exclusion rule could ever have addressed it.
        "fsck_errors": fsck_errors(),
    }


def fsck_errors() -> list[str]:
    """Object-database errors reported by `git fsck`.

    Only `error:` lines are retained. `dangling` objects are a normal consequence of
    ordinary history rewriting and are not corruption; treating them as findings would make
    the gate fire on healthy repositories and train readers to ignore it.
    """
    proc = subprocess.run(  # noqa: S603
        ["git", "fsck", "--no-progress"],  # noqa: S607 - fixed argv, no shell
        cwd=REPO,
        capture_output=True,
        text=True,
        check=False,
    )
    return [
        line.strip()
        for line in (proc.stdout + proc.stderr).splitlines()
        if line.startswith(("error:", "fatal:", "missing ", "broken "))
    ]


def contamination_state(decl: dict) -> dict:
    """Filesystem contamination, from the canonical repository-intelligence capability.

    UCOS-CL-001. This programme previously defined repository cleanliness as a count of
    `git status --porcelain` lines. That command applies the ignore authority, which made
    `.gitignore` an INPUT to the gate that polices excluded state: two lines added at
    be46a300 removed 41 physically-present files from the observation surface, flipped
    GATE-12 and GATE-04, opened this programme's gate, satisfied AEE OBS-BLUEPRINT-GATE
    and cleared CONV-02 — while every one of those files was still on disk.

    The measurement is NOT reimplemented here. `platform.repository_intelligence` is the
    repository's repository-state capability; this programme consumes it. Adding an ignore
    rule now adds a classification obligation in `00-BOOK/DATA/exclusion-register.json`
    rather than removing an observation, so the metric cannot be shrunk unilaterally.
    """
    # The repository root must lead sys.path or `platform` resolves to the STDLIB module of
    # that name and the capability is invisible. This engine is executed from its own
    # directory (`make rib`, and directly), so the root is not there by default — the
    # measurement silently fell back to fail-closed until this was added.
    root = str(REPO)
    if sys.path[:1] != [root]:
        sys.path.insert(0, root)
    try:
        from platform.repository_intelligence.contamination import measure
    except ImportError as exc:  # pragma: no cover - the capability ships with the repo
        return {"available": False, "reason": f"contamination capability unavailable: {exc}"}
    try:
        report = measure(REPO, generated=own_generated_paths(decl))
    except (OSError, RuntimeError) as exc:
        # Fail closed: an unmeasurable repository is not a clean one.
        return {"available": False, "reason": str(exc)}
    state = dict(report.as_dict())
    state["available"] = True
    return state


def tracked_conflicts() -> list[str]:
    out = git("diff", "--name-only", "--diff-filter=U")
    return [line for line in out.splitlines() if line.strip()]


def broken_symlinks() -> list[str]:
    found: list[str] = []
    for rel in tracked("."):
        path = REPO / rel
        if path.is_symlink() and not path.exists():
            found.append(rel)
    return sorted(found)


def table(headers: list[str], rows: list[list[str]]) -> str:
    if not rows:
        rows = [["\u2014"] * len(headers)]
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


def navigate(payload: object, pointer: str | None) -> object:
    """Walk a dotted pointer into parsed data. Returns None when it does not resolve."""
    if pointer in (None, ""):
        return payload
    current = payload
    for part in str(pointer).split("."):
        if isinstance(current, dict) and part in current:
            current = current[part]
        else:
            return None
    return current


def short(text: object, limit: int = 64) -> str:
    body = str(text).replace("|", "/").replace("\n", " ")
    return body if len(body) <= limit else body[: limit - 1] + "\u2026"


def dotted(path: str) -> str:
    return path.replace("/", ".")


# ------------------------------------------------------------------ substrate loading


class Substrate:
    """The declared machine-readable substrate, loaded once and never mutated."""

    def __init__(self, decl: dict) -> None:
        self.records: dict[str, dict] = {}
        self.payloads: dict[str, object] = {}
        for entry in section(decl, "substrate"):
            ident = str(entry.get("id") or "")
            rel = str(entry.get("path") or "")
            path = REPO / rel
            kind = str(entry.get("kind") or "")
            record = {
                "id": ident,
                "path": rel,
                "kind": kind,
                "purpose": entry.get("purpose") or "",
                "required": bool(entry.get("required")),
                "generated": bool(entry.get("generated")),
                "exists": path.is_file(),
                "tracked": is_tracked(rel) if rel else False,
                "parses": False,
                "pointers": [str(item) for item in as_list(entry.get("pointers"))],
                "pointers_resolved": [],
                "pointers_unresolved": [],
                "records": 0,
                "content_sha256": "",
            }
            payload: object | None = None
            if record["exists"]:
                raw = path.read_bytes()
                # UCOS-RFP-001 RFP-4 — a substrate the declaration marks GENERATED is
                # itself derived from the tracked tree, and this blueprint's own outputs
                # are part of that tree. Recording its content hash therefore closes a
                # cycle: the hash lands in a tracked artifact, which changes the tree the
                # generated substrate derives from, which changes the hash, without limit.
                # Measured: it did not converge over four successive commits. The hash of a
                # generated substrate is not reproducible provenance in any case, because
                # the commit does not carry the substrate. Its usability is still fully
                # evidenced — existence, parsing, resolved pointers and record count are all
                # recorded, and the only thing withheld is the one field that cannot hold
                # still.
                if not record["generated"]:
                    record["content_sha256"] = hashlib.sha256(raw).hexdigest()
                else:
                    record["content_sha256"] = (
                        "not recorded — generated substrate (UCOS-RFP-001 RFP-4)"
                    )
                try:
                    payload = tomllib.loads(raw.decode("utf-8")) if kind == "toml" else None
                    if payload is None:
                        payload = json.loads(raw.decode("utf-8"))
                    record["parses"] = True
                except (json.JSONDecodeError, tomllib.TOMLDecodeError, UnicodeDecodeError):
                    payload = None
            if payload is not None:
                self.payloads[ident] = payload
                for pointer in record["pointers"]:
                    value = navigate(payload, pointer)
                    if value is None:
                        record["pointers_unresolved"].append(pointer)
                    else:
                        record["pointers_resolved"].append(pointer)
                        if isinstance(value, list | dict):
                            record["records"] += len(value)
            self.records[ident] = record

    def payload(self, ident: str) -> object | None:
        return self.payloads.get(ident)

    def findings(self) -> list[str]:
        out: list[str] = []
        for ident in sorted(self.records):
            record = self.records[ident]
            if not record["required"]:
                continue
            if not record["exists"]:
                out.append(f"{ident}: required substrate absent: {record['path']}")
                continue
            if not record["parses"]:
                out.append(f"{ident}: required substrate does not parse: {record['path']}")
                continue
            if not record["tracked"] and not record["generated"]:
                out.append(f"{ident}: required substrate is not version-controlled")
            for pointer in record["pointers_unresolved"]:
                out.append(f"{ident}: declared pointer does not resolve: {pointer}")
        return out


def substrate_records(sub: Substrate, ident: str, pointer: str | None) -> list[dict]:
    value = navigate(sub.payload(ident), pointer)
    if isinstance(value, list):
        return [item for item in value if isinstance(item, dict)]
    if isinstance(value, dict):
        return [item for item in value.values() if isinstance(item, dict)]
    return []


# --------------------------------------------------------------------------- discovery


def truncate(path: str, depth: int) -> str:
    parts = [part for part in path.split("/") if part]
    return "/".join(parts[:depth]) if depth > 0 else path


def blank_unit(key: str, location: str, unit_class: str) -> dict:
    return {
        "unit_key": key,
        "unique_id": "",
        "canonical_name": key,
        "location": location,
        "unit_class": unit_class,
        "root": (location.split("/")[0] if location else ""),
        "leaf": (location.split("/")[-1] if location else key),
        "sources": [],
        "owner": "",
        "program": "",
        "phase": "",
        "lifecycle": "",
        "implementation_status": "",
        "declared": "",
        "source_files": 0,
        "tracked_files": 0,
        "unit_tests": 0,
        "evidence_assets": 0,
        "in_coverage_scope": False,
        "interfaces": 0,
        "interface_names": [],
        "registered_artifacts": 0,
        "corpus_artifacts": 0,
        "entrypoint_references": 0,
        "rie_id": "",
        "reachable_by": [],
        "dependencies": 0,
        "consumers": 0,
        "providers": 0,
        "dependency_units": [],
        "consumer_units": [],
        "degree": 0,
        "dependents": 0,
        "reachable": False,
        "is_test_unit": False,
        "duplicate_responsibility": False,
        "superseded_by": "",
        "unresolved_catalogue_record": False,
        "unregistered_and_closed": False,
        "disposition": "",
        "disposition_rule": "",
        "disposition_reason": "",
        "planes": [],
    }


def discover(decl: dict, sub: Substrate) -> tuple[dict[str, dict], list[dict]]:
    """Build the unit universe. Every unit originates in a declared discovery source."""
    units: dict[str, dict] = {}
    reports: list[dict] = []

    def touch(key: str, location: str, unit_class: str, source_id: str) -> dict:
        unit = units.get(key)
        if unit is None:
            unit = blank_unit(key, location, unit_class)
            units[key] = unit
        if not unit["location"] and location:
            unit["location"] = location
            unit["root"] = location.split("/")[0]
            unit["leaf"] = location.split("/")[-1]
        if source_id not in unit["sources"]:
            unit["sources"].append(source_id)
        return unit

    for entry in section(decl, "discovery"):
        ident = str(entry.get("id") or "")
        kind = str(entry.get("kind") or "")
        unit_class = str(entry.get("class") or "")
        produced: list[str] = []
        probed = 0
        if kind == "tracked_glob_unit":
            paths = tracked(str(entry.get("selector") or ""))
            probed = len(paths)
            depth = int(entry.get("key_depth") or 1)
            for rel in paths:
                location = truncate(rel, depth)
                if not location:
                    continue
                key = dotted(location)
                touch(key, location, unit_class, ident)
                if key not in produced:
                    produced.append(key)
        elif kind == "substrate_unit":
            records = substrate_records(
                sub, str(entry.get("substrate") or ""), entry.get("pointer")
            )
            probed = len(records)
            key_field = str(entry.get("key_field") or "")
            location_field = entry.get("location_field")
            field_map = entry.get("fields") or {}
            for record in records:
                raw_location = str(record.get(str(location_field)) or "") if location_field else ""
                key = dotted(raw_location) if raw_location else str(record.get(key_field) or "")
                if not key:
                    continue
                unit = touch(key, raw_location, unit_class, ident)
                if raw_location and not is_tracked(raw_location):
                    unit["unresolved_catalogue_record"] = True
                for target, origin in field_map.items():
                    value = record.get(str(origin))
                    if value is not None and not unit.get(str(target)):
                        unit[str(target)] = value
                if key not in produced:
                    produced.append(key)
        else:
            fail_closed(f"{ident}: declares an unimplemented discovery kind: {kind!r}")
        reports.append(
            {
                "id": ident,
                "kind": kind,
                "class": unit_class,
                "selector": str(entry.get("selector") or entry.get("pointer") or ""),
                "purpose": entry.get("purpose") or "",
                "probed": probed,
                "units": len(produced),
                "sample": sorted(produced)[:4],
            }
        )
    return units, reports


def enrich(decl: dict, sub: Substrate, units: dict[str, dict]) -> list[dict]:
    reports: list[dict] = []
    by_location = {unit["location"]: unit for unit in units.values() if unit["location"]}
    for entry in section(decl, "enrichment"):
        ident = str(entry.get("id") or "")
        records = substrate_records(sub, str(entry.get("substrate") or ""), entry.get("pointer"))
        match_field = str(entry.get("match_field") or "")
        mode = str(entry.get("match_mode") or "")
        field_map = entry.get("fields") or {}
        matched = 0
        for record in records:
            probe = str(record.get(match_field) or "")
            if not probe:
                continue
            target: dict | None = None
            if mode == "path_prefix":
                best = ""
                for location, unit in by_location.items():
                    if probe == location or probe.startswith(location + "/"):
                        if len(location) > len(best):
                            best, target = location, unit
            elif mode == "unit_key_dotted":
                target = units.get(dotted(probe))
            if target is None:
                continue
            matched += 1
            for key, origin in field_map.items():
                value = record.get(str(origin))
                if value is not None and not target.get(str(key)):
                    target[str(key)] = value
        reports.append(
            {
                "id": ident,
                "purpose": entry.get("purpose") or "",
                "records": len(records),
                "matched": matched,
            }
        )
    return reports


def measure(decl: dict, sub: Substrate, units: dict[str, dict]) -> list[dict]:
    reports: list[dict] = []
    entrypoint_text = "\n".join(
        (REPO / rel).read_text("utf-8", errors="replace")
        for entry in section(decl, "entrypoints")
        for rel in tracked(str(entry.get("selector") or ""))
        if (REPO / rel).is_file()
    )
    # An interface belongs to the deepest unit that contains its target, never to every
    # ancestor: attributing one entry point to a root and a package alike would manufacture
    # a duplicate that does not exist.
    ordered_locations = sorted(
        ((unit["location"], key) for key, unit in units.items() if unit["location"]),
        key=lambda pair: -len(pair[0]),
    )
    for entry in section(decl, "measures"):
        ident = str(entry.get("id") or "")
        kind = str(entry.get("kind") or "")
        field = str(entry.get("field") or "")
        total = 0
        covered = 0
        interface_owner: dict[str, str] = {}
        owned: dict[str, int] = {}
        if kind == "owned_source_count":
            pathspecs = [str(entry.get("selector") or "")] + [
                str(item) for item in as_list(entry.get("exclude"))
            ]
            for rel in tracked(*pathspecs):
                for location, key in ordered_locations:
                    if rel == location or rel.startswith(location + "/"):
                        owned[key] = owned.get(key, 0) + 1
                        break
        if kind == "substrate_map_prefix":
            declared = navigate(
                sub.payload(str(entry.get("substrate") or "")), entry.get("pointer")
            )
            if isinstance(declared, dict):
                for name, target in sorted(declared.items()):
                    text = str(target).split(":")[0]
                    for location, key in ordered_locations:
                        prefix = dotted(location)
                        if text == prefix or text.startswith(prefix + "."):
                            interface_owner[str(name)] = key
                            break
        for key, unit in units.items():
            value: Any = 0
            if kind == "tracked_glob_count":
                templates = [
                    str(item)
                    for item in (
                        as_list(entry.get("selector_templates"))
                        or as_list(entry.get("selector_template"))
                    )
                ]
                excludes = [str(item) for item in as_list(entry.get("exclude_templates"))]
                if unit["location"]:
                    seen: set[str] = set()
                    for template in templates:
                        pathspecs = [
                            item.replace("{location}", unit["location"])
                            .replace("{root}", unit["root"])
                            .replace("{leaf}", unit["leaf"])
                            for item in [template, *excludes]
                        ]
                        seen |= set(tracked(*pathspecs))
                    value = len(seen)
            elif kind == "substrate_list_member":
                declared = navigate(
                    sub.payload(str(entry.get("substrate") or "")), entry.get("pointer")
                )
                members = {str(item) for item in as_list(declared)}
                value = bool(unit["location"]) and unit["location"] in members
            elif kind == "substrate_map_prefix":
                names = sorted(name for name, owner in interface_owner.items() if owner == key)
                unit["interface_names"] = names
                value = len(names)
            elif kind == "substrate_record_prefix":
                records = substrate_records(
                    sub, str(entry.get("substrate") or ""), entry.get("pointer")
                )
                record_field = str(entry.get("record_field") or "")
                if unit["location"]:
                    value = len(
                        [
                            record
                            for record in records
                            if str(record.get(record_field) or "").startswith(unit["location"])
                        ]
                    )
            elif kind == "owned_source_count":
                value = owned.get(key, 0)
            elif kind == "text_reference_count":
                if unit["location"]:
                    value = entrypoint_text.count(unit["location"])
                    # A file-granularity unit is normally invoked by basename from inside
                    # the directory that holds it, so the full path never appears. Counting
                    # the leaf as well is what keeps a live tool from reading as dead — but
                    # only for a unit that IS a file: a directory leaf such as a test folder
                    # is a common word, and counting it would manufacture reachability.
                    files, _dirs = tracked_universe()
                    if entry.get("match_leaf") and unit["location"] in files:
                        value += entrypoint_text.count(unit["leaf"])
            else:
                fail_closed(f"{ident}: declares an unimplemented measure kind: {kind!r}")
            unit[field] = value
            if isinstance(value, bool):
                covered += 1 if value else 0
                total += 1 if value else 0
            else:
                total += int(value)
                covered += 1 if value else 0
        reports.append(
            {
                "id": ident,
                "kind": kind,
                "field": field,
                "purpose": entry.get("purpose") or "",
                "units_with_value": covered,
                "total": total,
            }
        )
    return reports


# ------------------------------------------------------------------------------ planes


def _typing_guard(node: ast.If) -> bool:
    test = node.test
    if isinstance(test, ast.Name) and test.id == "TYPE_CHECKING":
        return True
    return isinstance(test, ast.Attribute) and test.attr == "TYPE_CHECKING"


def _imports(path: Path, exclude_guard: bool) -> list[str]:
    """Return the IMPORT-TIME module names imported by ``path``.

    Import-time, not every ``Import`` node reachable in the tree. These edges feed
    ``PLN-CODE`` and ``PLN-MODULE`` — the two planes that decide the acyclicity rule —
    and a cycle is a property of module *initialisation*. Two import forms are
    provably incapable of closing one:

      * ``if TYPE_CHECKING:`` — erased before the interpreter resolves anything;
      * an import inside a function or class body — resolved on first call, by which
        time every module in the loop is already fully initialised.

    This is not a relaxation of the acyclicity rule; it is the rule as the repository's
    canonical owner of the dependency dimension already states it.
    ``platform/repository_intelligence/substrate.py`` separates ``import_time_imports``
    from ``imports`` for exactly this reason, and
    ``platform/repository_intelligence/discovery.py`` records that reading ``imports``
    here "reported both recorded cycles against code that was already decoupled on
    purpose" — naming the ``universal_foundation -> universal_measurement ->
    universal_ownership`` loop closed by a single function-local import in
    ``universal_ownership/cli.py``, which is one of the five this engine reported.

    Counting a deferred import as an import-time edge reports the cure for a circular
    import as the circular import. Measured on this corpus: five ``CYC-ARCHITECTURAL``
    cycles under the every-node rule, zero under this one, while ``PLN-MODULE`` — the
    plane where a true Python import cycle would break execution — reported zero
    non-benign cycles under either. No true cycle is hidden by this rule, because a
    true cycle is by construction made of import-time edges.
    """
    try:
        tree = ast.parse(path.read_text("utf-8"))
    except (OSError, SyntaxError, UnicodeDecodeError):
        return []
    skip: set[int] = set()
    if exclude_guard:
        for node in ast.walk(tree):
            if isinstance(node, ast.If) and _typing_guard(node):
                for statement in node.body:
                    for inner in ast.walk(statement):
                        skip.add(id(inner))
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef | ast.ClassDef):
            for statement in node.body:
                for inner in ast.walk(statement):
                    skip.add(id(inner))
    names: list[str] = []
    for node in ast.walk(tree):
        if id(node) in skip:
            continue
        if isinstance(node, ast.Import):
            names += [alias.name for alias in node.names]
        elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
            names.append(node.module)
    return names


def _cycles(adjacency: dict[str, set[str]]) -> list[list[str]]:
    colour: dict[str, int] = dict.fromkeys(adjacency, 0)
    found: list[list[str]] = []
    limit = sys.getrecursionlimit()
    sys.setrecursionlimit(max(limit, 20000))

    def walk(node: str, stack: list[str]) -> None:
        colour[node] = 1
        stack.append(node)
        for nxt in sorted(adjacency.get(node, ())):
            if colour.get(nxt, 0) == 1:
                found.append(stack[stack.index(nxt) :] + [nxt])
            elif colour.get(nxt, 0) == 0:
                walk(nxt, stack)
        stack.pop()
        colour[node] = 2

    for node in sorted(adjacency):
        if colour.get(node, 0) == 0:
            walk(node, [])
    sys.setrecursionlimit(limit)
    return found


def classify_cycles(decl: dict, cycles: list[list[str]], owner_of: dict[str, str]) -> list[dict]:
    classes = section(decl, "cycle_classes")
    out: list[dict] = []
    for cycle in cycles:
        owners = {owner_of.get(node, node) for node in cycle}
        assigned: dict | None = None
        for entry in classes:
            rule = str(entry.get("rule") or "")
            if rule == "package_init_reexport" and len(owners) == 1:
                assigned = entry
                break
            if rule == "cross_unit" and len(owners) > 1:
                assigned = entry
                break
        out.append(
            {
                "cycle": cycle,
                "class": str((assigned or {}).get("id") or ""),
                "benign": bool((assigned or {}).get("benign")),
                "units": sorted(owners),
            }
        )
    return out


def build_planes(decl: dict, sub: Substrate, units: dict[str, dict]) -> list[dict]:
    planes: list[dict] = []
    for entry in section(decl, "planes"):
        ident = str(entry.get("id") or "")
        kind = str(entry.get("kind") or "")
        unit_class = str(entry.get("unit_class") or "")
        guard = bool(entry.get("exclude_typing_guard"))
        adjacency: dict[str, set[str]] = {}
        owner_of: dict[str, str] = {}
        unresolved = 0
        edge_sites: dict[tuple[str, str], list[str]] = {}

        if kind in ("python_import_graph", "python_module_graph"):
            members = {
                unit["unit_key"]: unit
                for unit in units.values()
                if unit["unit_class"] == unit_class and unit["location"]
            }
            # deepest location wins, so a package is attributed to itself, not its root
            locations = sorted(
                ((unit["location"], key) for key, unit in members.items()),
                key=lambda pair: -len(pair[0]),
            )

            def owning_unit(rel: str, table: list[tuple[str, str]] = locations) -> str:
                for location, key in table:
                    if rel == location or rel.startswith(location + "/"):
                        return key
                return ""

            files = list(tracked(":(glob)**/*.py"))
            if kind == "python_module_graph":
                index: dict[str, str] = {}
                for rel in files:
                    module = dotted(rel[:-3])
                    if module.endswith(".__init__"):
                        module = module[: -len(".__init__")]
                    index[module] = rel
                for module, rel in sorted(index.items()):
                    holder = owning_unit(rel)
                    if not holder:
                        continue
                    owner_of[module] = holder
                    adjacency.setdefault(module, set())
                    for name in _imports(REPO / rel, guard):
                        probe = name
                        while probe and probe not in index:
                            probe = probe.rsplit(".", 1)[0] if "." in probe else ""
                        if probe and probe != module:
                            adjacency[module].add(probe)
                            adjacency.setdefault(probe, set())
            else:
                prefixes = {dotted(unit["location"]): key for key, unit in members.items()}
                for key in members:
                    adjacency.setdefault(key, set())
                    owner_of[key] = key
                for rel in files:
                    holder = owning_unit(rel)
                    if not holder:
                        continue
                    for name in _imports(REPO / rel, guard):
                        probe = name
                        target = ""
                        while probe:
                            if probe in prefixes:
                                target = prefixes[probe]
                                break
                            probe = probe.rsplit(".", 1)[0] if "." in probe else ""
                        if target and target != holder:
                            adjacency[holder].add(target)
                            edge_sites.setdefault((holder, target), []).append(rel)
        elif kind == "typed_edge_graph":
            records = substrate_records(
                sub, str(entry.get("substrate") or ""), entry.get("pointer")
            )
            from_field = str(entry.get("from_field") or "")
            to_field = str(entry.get("to_field") or "")
            type_field = str(entry.get("type_field") or "")
            wanted = {str(item) for item in as_list(entry.get("dependency_types"))}
            known = {str(record.get(from_field) or "") for record in records}
            known |= {str(record.get(to_field) or "") for record in records}
            for record in records:
                if str(record.get(type_field) or "") not in wanted:
                    continue
                source = str(record.get(from_field) or "")
                target = str(record.get(to_field) or "")
                if not source or not target:
                    unresolved += 1
                    continue
                if target not in known:
                    unresolved += 1
                    continue
                adjacency.setdefault(source, set()).add(target)
                adjacency.setdefault(target, set())
                owner_of.setdefault(source, source)
                owner_of.setdefault(target, target)
        else:
            fail_closed(f"{ident}: declares an unimplemented plane kind: {kind!r}")

        cycles = classify_cycles(decl, _cycles(adjacency), owner_of)
        inbound: dict[str, set[str]] = {node: set() for node in adjacency}
        for source, targets in adjacency.items():
            for target in targets:
                inbound.setdefault(target, set()).add(source)
        planes.append(
            {
                "id": ident,
                "kind": kind,
                "purpose": entry.get("purpose") or "",
                "nodes": len(adjacency),
                "edges": sum(len(value) for value in adjacency.values()),
                "unresolved_edges": unresolved,
                "cycles": cycles,
                "architectural_cycles": [item for item in cycles if not item["benign"]],
                "adjacency": {key: sorted(value) for key, value in sorted(adjacency.items())},
                "inbound": {key: sorted(value) for key, value in sorted(inbound.items())},
                "edge_sites": {
                    f"{pair[0]} -> {pair[1]}": sorted(set(value))[:3]
                    for pair, value in sorted(edge_sites.items())
                },
                "unit_class": unit_class,
            }
        )
    return planes


def apply_planes(decl: dict, units: dict[str, dict], planes: list[dict]) -> None:
    for plane in planes:
        adjacency = plane["adjacency"]
        inbound = plane["inbound"]
        for key, unit in units.items():
            if key not in adjacency and key not in inbound:
                continue
            out = adjacency.get(key, [])
            back = inbound.get(key, [])
            unit["dependency_units"] = sorted(set(unit["dependency_units"]) | set(out))
            unit["consumer_units"] = sorted(set(unit["consumer_units"]) | set(back))
            if plane["id"] not in unit["planes"]:
                unit["planes"].append(plane["id"])
    dimensions = [str(entry.get("field") or "") for entry in section(decl, "reachability")]
    for unit in units.values():
        unit["dependencies"] = len(unit["dependency_units"])
        unit["consumers"] = len(unit["consumer_units"])
        unit["providers"] = len(unit["dependency_units"])
        unit["degree"] = unit["dependencies"] + unit["consumers"]
        unit["reachable_by"] = [field for field in dimensions if unit.get(field)]
        unit["reachable"] = bool(unit["reachable_by"])


def transitive_dependents(units: dict[str, dict]) -> None:
    reverse: dict[str, set[str]] = {key: set() for key in units}
    for key, unit in units.items():
        for target in unit["dependency_units"]:
            reverse.setdefault(target, set()).add(key)
    for key, unit in units.items():
        seen: set[str] = set()
        frontier = list(reverse.get(key, ()))
        while frontier:
            node = frontier.pop()
            if node in seen:
                continue
            seen.add(node)
            frontier += [item for item in reverse.get(node, ()) if item not in seen]
        unit["dependents"] = len(seen)


# ------------------------------------------------------------------------- duplicates


def detect_duplicates(decl: dict, sub: Substrate, units: dict[str, dict]) -> list[dict]:
    out: list[dict] = []
    engine_selectors = [
        (str(entry.get("selector") or ""), int(entry.get("key_depth") or 1))
        for entry in section(decl, "discovery")
        if str(entry.get("kind")) == "tracked_glob_unit" and entry.get("selector")
    ]
    for entry in section(decl, "duplicates"):
        rule = str(entry.get("rule") or "")
        findings: list[dict] = []
        buckets: dict[str, list[str]] = {}
        if rule == "leaf_collision":
            for key, unit in units.items():
                if unit["source_files"]:
                    buckets.setdefault(unit["leaf"], []).append(key)
        elif rule == "catalogue_collision":
            for key, unit in units.items():
                if unit.get("rie_id"):
                    buckets.setdefault(unit["location"] or key, []).append(str(unit["rie_id"]))
        elif rule == "interface_collision":
            for key, unit in units.items():
                for name in unit["interface_names"]:
                    buckets.setdefault(name, []).append(key)
        elif rule == "location_collision":
            for key, unit in units.items():
                if unit["location"]:
                    buckets.setdefault(unit["location"], []).append(key)
        elif rule == "engine_collision":
            for selector, depth in engine_selectors:
                for rel in tracked(selector):
                    if rel.endswith(".py") and "_engine" in Path(rel).name:
                        buckets.setdefault(truncate(rel, depth), []).append(rel)
        elif rule == "record_field_collision":
            records = substrate_records(
                sub, str(entry.get("substrate") or ""), entry.get("pointer")
            )
            field = str(entry.get("field") or "")
            label = str(entry.get("label_field") or field)
            scope_field = entry.get("scope_field")
            scope_prefix = str(entry.get("scope_prefix") or "")
            exclude_prefix = str(entry.get("exclude_prefix") or "")
            for record in records:
                located = str(record.get(label) or "")
                if scope_field is not None and not str(
                    record.get(str(scope_field)) or ""
                ).startswith(scope_prefix):
                    continue
                if exclude_prefix and located.startswith(exclude_prefix):
                    continue
                value = str(record.get(field) or "")
                if value:
                    buckets.setdefault(value, []).append(located or value)
        elif rule == "substrate_field_value_count":
            records = substrate_records(
                sub, str(entry.get("substrate") or ""), entry.get("pointer")
            )
            field = str(entry.get("field") or "")
            wanted = str(entry.get("value") or "")
            hits = [record for record in records if str(record.get(field) or "") == wanted]
            findings = [{"subject": wanted, "members": []} for _ in hits]
        elif rule == "substrate_counter":
            counted = navigate(sub.payload(str(entry.get("substrate") or "")), entry.get("pointer"))
            total = int(counted) if isinstance(counted, int | float) else 0
            findings = [
                {"subject": str(entry.get("pointer") or ""), "members": []} for _ in range(total)
            ]
        else:
            fail_closed(f"{entry.get('id')}: declares an unimplemented duplicate rule: {rule!r}")
        if not findings:
            findings = [
                {"subject": short(name, 96), "members": sorted(members)}
                for name, members in sorted(buckets.items())
                if len(members) > 1
            ]
        out.append(
            {
                "id": str(entry.get("id") or ""),
                "class": str(entry.get("class") or ""),
                "blocking": bool(entry.get("blocking")),
                "subject": entry.get("subject") or "",
                "rule": rule,
                "findings": findings,
                "count": len(findings),
            }
        )
    # Only a BLOCKING class may accuse a unit of duplicate responsibility. An advisory
    # signal — a shared leaf name across layers, a staged programme owning one engine per
    # phase — is recorded and counted, but it drives no disposition, because a name is not
    # a responsibility and a phase is not a duplicate.
    for record in out:
        if not record["blocking"]:
            continue
        for finding in record["findings"]:
            for member in finding["members"]:
                if member in units:
                    units[member]["duplicate_responsibility"] = True
    return out


# ------------------------------------------------------------------------ disposition


PREDICATES: dict[str, Callable[[Any, Any], bool]] = {
    "truthy": lambda value, _expected: bool(value),
    "falsy": lambda value, _expected: not bool(value),
    "equals": lambda value, expected: value == expected,
    "not_equals": lambda value, expected: value != expected,
    "in": lambda value, expected: value in as_list(expected),
    "not_in": lambda value, expected: value not in as_list(expected),
    "contains": lambda value, expected: str(expected) in str(value),
    "greater_than": lambda value, expected: _number(value) > _number(expected),
    "less_than": lambda value, expected: _number(value) < _number(expected),
    "exists": lambda value, _expected: value not in (None, ""),
    "absent": lambda value, _expected: value in (None, ""),
}


def _number(value: Any) -> float:
    if isinstance(value, bool):
        return 1.0 if value else 0.0
    if isinstance(value, int | float):
        return float(value)
    try:
        return float(str(value))
    except ValueError:
        return 0.0


def matches(unit: dict, clause: dict) -> bool:
    op = str(clause.get("op") or "")
    predicate = PREDICATES.get(op)
    if predicate is None:
        fail_closed(f"declares an unimplemented predicate: {op!r}")
    return predicate(unit.get(str(clause.get("field") or "")), clause.get("value"))


def assign_dispositions(decl: dict, units: dict[str, dict]) -> list[dict]:
    rules = section(decl, "disposition_rules")
    tally: dict[str, int] = {}
    for unit in units.values():
        for rule in rules:
            clauses = [item for item in as_list(rule.get("when")) if isinstance(item, dict)]
            if all(matches(unit, clause) for clause in clauses):
                unit["disposition"] = str(rule.get("disposition") or "")
                unit["disposition_rule"] = str(rule.get("id") or "")
                unit["disposition_reason"] = str(rule.get("because") or "")
                break
        tally[unit["disposition_rule"]] = tally.get(unit["disposition_rule"], 0) + 1
    return [
        {
            "id": str(rule.get("id") or ""),
            "disposition": str(rule.get("disposition") or ""),
            "because": rule.get("because") or "",
            "clauses": len([item for item in as_list(rule.get("when")) if isinstance(item, dict)]),
            "units": tally.get(str(rule.get("id") or ""), 0),
        }
        for rule in rules
    ]


# ------------------------------------------------------------------------------- gaps


def detect_gaps(decl: dict, units: dict[str, dict]) -> list[dict]:
    out: list[dict] = []
    for entry in section(decl, "gaps"):
        restrict = str(entry.get("restrict_class") or "")
        clause = {"field": entry.get("field"), "op": entry.get("op"), "value": entry.get("value")}
        members = sorted(
            key
            for key, unit in units.items()
            if (not restrict or unit["unit_class"] == restrict) and matches(unit, clause)
        )
        out.append(
            {
                "id": str(entry.get("id") or ""),
                "class": str(entry.get("class") or ""),
                "subject": entry.get("subject") or "",
                "restrict_class": restrict,
                "count": len(members),
                "members": members,
            }
        )
    return out


# ------------------------------------------------------------------------------ queue


def build_queue(decl: dict, units: dict[str, dict]) -> dict:
    queued_flags = {
        str(entry.get("disposition")): bool(entry.get("consumes_queue"))
        for entry in section(decl, "dispositions")
    }
    queued = {
        key: unit for key, unit in units.items() if queued_flags.get(unit["disposition"], False)
    }
    waves: list[list[str]] = []
    placed: set[str] = set()
    remaining = dict(queued)
    while remaining:
        wave = sorted(
            key
            for key, unit in remaining.items()
            if not [
                dep
                for dep in unit["dependency_units"]
                if dep in remaining and dep != key and dep not in placed
            ]
        )
        if not wave:
            wave = sorted(remaining)  # a cycle inside the queue: emitted as one band
        waves.append(wave)
        placed |= set(wave)
        for key in wave:
            remaining.pop(key, None)
    depth: dict[str, int] = {}
    for index, wave in enumerate(waves):
        for key in wave:
            depth[key] = index + 1
    ordered = sorted(
        queued.values(),
        key=lambda unit: (
            depth.get(unit["unit_key"], 0),
            -int(unit["dependents"]),
            -int(unit["consumers"]),
            unit["unit_key"],
        ),
    )
    critical = [
        unit["unit_key"]
        for unit in sorted(
            queued.values(),
            key=lambda unit: (
                -int(unit["dependents"]),
                depth.get(unit["unit_key"], 0),
                unit["unit_key"],
            ),
        )[:10]
    ]
    return {
        "queued_total": len(queued),
        "waves": [
            {
                "wave": index + 1,
                "units": wave,
                "parallel": len(wave),
                "blocked_by": sorted(
                    {
                        dep
                        for key in wave
                        for dep in units[key]["dependency_units"]
                        if dep in queued and depth.get(dep, 0) < index + 1
                    }
                ),
            }
            for index, wave in enumerate(waves)
        ],
        "priority": [
            {
                "rank": index + 1,
                "unit_key": unit["unit_key"],
                "disposition": unit["disposition"],
                "wave": depth.get(unit["unit_key"], 0),
                "dependents": unit["dependents"],
            }
            for index, unit in enumerate(ordered)
        ],
        "critical_path": critical,
        "max_parallel": max((len(wave) for wave in waves), default=0),
    }


# --------------------------------------------------------------------------- matrices


def build_matrices(decl: dict, units: dict[str, dict]) -> list[dict]:  # noqa: C901
    """Bind or derive each declared matrix.

    A matrix declared BOUND emits a pointer to the canonical owner and no rows of its
    own: that is what makes the binding a reuse rather than a restatement. ``restated``
    is therefore a measurement, not a preference — a bound matrix that carries rows here
    would be a duplicate truth, and the no-duplicate-truth obligation counts exactly that.
    """
    declared_substrate = {str(entry.get("path")) for entry in section(decl, "substrate")}
    out: list[dict] = []
    for entry in section(decl, "matrices"):
        owner = entry.get("canonical_owner")
        resolved = resolve_reference(str(owner)) if owner else None
        mode = str(entry.get("mode") or "")
        is_bound = mode == "BOUND"
        rows = 0 if is_bound else len(units)
        owner_form = (
            "machine-readable substrate, extended here beyond the coverage it holds"
            if str(owner) in declared_substrate
            else "located, but not in machine-readable form, so it cannot be bound by pointer"
        )
        out.append(
            {
                "id": str(entry.get("id") or ""),
                "index": int(entry.get("index") or 0),
                "name": str(entry.get("name") or ""),
                "subject": entry.get("subject") or "",
                "mode": mode,
                "canonical_owner": str(owner) if owner else "",
                "owner_form": owner_form if owner else "",
                "owner_resolves": resolved is not None,
                "is_bound": is_bound,
                "restated": bool(is_bound and rows),
                "resolves": (resolved is not None) if owner else (not is_bound),
                "columns": [str(item) for item in as_list(entry.get("columns"))],
                "rows": rows,
            }
        )
    return out


# ------------------------------------------------------------------------- assessment


def _scalar_substrate(sub: Substrate, marker: str) -> dict | None:
    for ident in sorted(sub.payloads):
        payload = sub.payloads[ident]
        if isinstance(payload, dict) and marker in payload:
            return payload
    return None


def compute_metrics(
    decl: dict,
    sub: Substrate,
    units: dict[str, dict],
    discovery: list[dict],
    planes: list[dict],
    duplicates: list[dict],
    gaps: list[dict],
    matrices: list[dict],
    probes: list[dict],
    repo: dict,
) -> dict:
    dispositions = {str(entry.get("disposition")) for entry in section(decl, "dispositions")}
    catalogue_records = 0
    for entry in section(decl, "discovery"):
        if str(entry.get("kind")) == "substrate_unit" and entry.get("location_field"):
            catalogue_records = len(
                substrate_records(sub, str(entry.get("substrate") or ""), entry.get("pointer"))
            )
    register_payload = _scalar_substrate(sub, "artifacts")
    register = (register_payload or {}).get("artifacts") if register_payload else None
    register_declared = int((register_payload or {}).get("count") or 0)
    dead_registry = 0
    if isinstance(register, list):
        dead_registry = len(
            [item for item in register if not is_tracked(str(item.get("path") or ""))]
        )
    cert = _scalar_substrate(sub, "domains_total") or {}
    certification_failed = int(cert.get("domains_total") or 0) - int(
        cert.get("domains_passed") or 0
    )
    certification_absent = 0 if cert.get("verdict") else 1
    closure = _scalar_substrate(sub, "gap_total") or {}
    closure_gaps = int(closure.get("gap_total") or 0)
    counters = closure.get("gaps")
    closure_duplicates = (
        int(counters.get("duplicate_canonical_homes") or 0) if isinstance(counters, dict) else 0
    )
    planning = _scalar_substrate(sub, "unresolved_total") or {}
    planning_unresolved = int(planning.get("unresolved_total") or 0)

    implementation_class = ""
    for entry in section(decl, "planes"):
        if entry.get("unit_class"):
            implementation_class = str(entry.get("unit_class"))
            break
    implemented = [unit for unit in units.values() if unit["unit_class"] == implementation_class]
    uncatalogued = sorted(
        unit["unit_key"] for unit in implemented if unit["source_files"] and not unit.get("rie_id")
    )
    orphans = sorted(unit["unit_key"] for unit in units.values() if not unit["reachable"])
    declared_scripts: dict[str, str] = {}
    for entry in section(decl, "measures"):
        if str(entry.get("kind")) == "substrate_map_prefix":
            value = navigate(sub.payload(str(entry.get("substrate") or "")), entry.get("pointer"))
            if isinstance(value, dict):
                declared_scripts = {str(k): str(v) for k, v in value.items()}
    module_index: set[str] = set()
    for rel in tracked(":(glob)**/*.py"):
        name = dotted(rel[:-3])
        module_index.add(name)
        if name.endswith(".__init__"):
            module_index.add(name[: -len(".__init__")])
    dead_interfaces = sorted(
        name
        for name, target in declared_scripts.items()
        if str(target).split(":")[0] not in module_index
    )
    integrity: list[str] = []
    if repo["conflicts"]:
        integrity.append(f"{repo['conflicts']} unresolved merge conflict(s)")
    if repo["detached"]:
        integrity.append("HEAD is detached")
    if repo["interrupted_operations"]:
        integrity.append(
            "partially applied operation: " + ", ".join(repo["interrupted_operations"])
        )
    if repo["broken_symlinks"]:
        integrity.append(f"{len(repo['broken_symlinks'])} broken symlink(s)")
    # UCOS-CL-003 — object-database corruption is a repository-integrity finding. Without
    # this, GATE-02 reported PASS while `git fsck` reported badRefName on a malformed ref
    # that broke every whole-history traversal in the repository.
    for finding in repo.get("fsck_errors", []):
        integrity.append(f"git fsck: {finding}")
    integrity += sub.findings()

    owner_collisions = 0
    for record in duplicates:
        if record["rule"] == "location_collision":
            owner_collisions = record["count"]
    unresolved_edges = sum(plane["unresolved_edges"] for plane in planes)
    architectural = sum(len(plane["architectural_cycles"]) for plane in planes)
    # Absence namespaces: for every unit field a registered refusal excuses, report both
    # the raw absence and the absence that is NOT covered by that refusal. A declared,
    # probed, owner-attributed refusal is the honest answer — not a silent zero, and not a
    # fabricated value.
    probed = {item["id"]: item for item in probes}
    bounded_fields: dict[str, bool] = {}
    for entry in section(decl, "non_derivable"):
        field = str(entry.get("bounds_field") or "")
        if not field:
            continue
        probe = probed.get(str(entry.get("probe") or ""))
        # The refusal excuses the absence only if its probe actually ran and measured the
        # substrate it claims to have searched. An unexecuted probe excuses nothing.
        bounded_fields[field] = bool(probe and probe["probed"] > 0)
    absence: dict[str, int] = {}
    for field, excused in sorted(bounded_fields.items()):
        raw = len([unit for unit in units.values() if not unit.get(field)])
        absence[f"absent:{field}"] = raw
        absence[f"absent_unbounded:{field}"] = 0 if excused else raw
    metrics = {
        "unit_total": len(units),
        "units_without_disposition": len([u for u in units.values() if not u["disposition"]]),
        "dispositions_outside_set": len(
            [u for u in units.values() if u["disposition"] and u["disposition"] not in dispositions]
        ),
        "discovery_sources_empty": len([item for item in discovery if not item["units"]]),
        "unresolved_dependency_edges": unresolved_edges,
        "owner_collisions": owner_collisions,
        "closure_duplicate_homes": closure_duplicates,
        "closure_gaps": closure_gaps,
        "matrix_duplication": len([record for record in matrices if record["restated"]]),
        "architectural_cycles": architectural,
        "benign_cycles": sum(
            len(plane["cycles"]) - len(plane["architectural_cycles"]) for plane in planes
        ),
        "orphan_units": len(orphans),
        "orphan_members": orphans,
        "dead_registry_entries": dead_registry,
        "dead_interfaces": len(dead_interfaces),
        "dead_interface_members": dead_interfaces,
        "duplicate_findings": sum(record["count"] for record in duplicates if record["blocking"]),
        "advisory_duplicate_signals": sum(
            record["count"] for record in duplicates if not record["blocking"]
        ),
        "unresolved_catalogue_records": len(
            [unit for unit in units.values() if unit["unresolved_catalogue_record"]]
        ),
        "uncatalogued_units": len(uncatalogued),
        "uncatalogued_members": uncatalogued,
        "catalogue_records": catalogue_records,
        "registration_drift": abs(len(register or []) - register_declared),
        "certification_domains_failed": certification_failed,
        "certification_verdict_absent": certification_absent,
        "planning_unresolved": planning_unresolved,
        "units_outside_architecture": len([u for u in units.values() if not u["unit_class"]]),
        "units_without_program": len([u for u in units.values() if not u["program"]]),
        "universes_unresolved": len([u for u in units.values() if not u["sources"]]),
        "realized_without_source": len(
            [
                u
                for u in units.values()
                if str(u.get("rie_status") or "")
                and not u["source_files"]
                and not u["tracked_files"]
            ]
        ),
        "matrices_unbound": len([record for record in matrices if not record["resolves"]]),
        "integrity_findings": len(integrity),
        "integrity_members": integrity,
        "dirty_entries": repo["dirty_entries"],
        "gap_findings": sum(record["count"] for record in gaps),
    }
    metrics.update(absence)
    # Repository cleanliness excludes THIS programme's own regenerated artifacts, and
    # nothing else. Those files are the deterministic output of the very command being
    # gated — byte-identical for an unchanged repository state, which --check-determinism
    # proves independently — so counting them would make the gate unsatisfiable by
    # construction. The authored declaration, engine and README are NOT excluded: an
    # uncommitted change to them is real repository dirt and is counted as such. The raw
    # figure stays visible beside the narrowed one, so nothing is hidden.
    metrics["generated_artifact_paths"] = sorted(own_generated_paths(decl))
    metrics["dirty_entries_outside_generated"] = repo["dirty_entries"]
    # UCOS-CL-001 — the contamination metrics. `dirty_entries_outside_generated` is
    # retained unchanged so nothing that reads it changes meaning; these ADD the
    # observation surface that the porcelain-only measurement never had.
    contam = repo.get("contamination") or {}
    metrics["contamination_available"] = bool(contam.get("available"))
    metrics["ignored_unclassified"] = (
        int(contam.get("ignored_unclassified", 0)) if contam.get("available") else 1
    )
    metrics["shadowed_tracked_paths_count"] = (
        int(contam.get("shadowed_tracked", 0)) if contam.get("available") else 1
    )
    metrics["contamination_entries"] = (
        int(contam.get("contamination_entries", 0)) if contam.get("available") else 1
    )
    metrics["contamination_unclassified_members"] = list(contam.get("unclassified_paths", []))
    metrics["contamination_shadowed_members"] = list(contam.get("shadowed_tracked_paths", []))
    for record in gaps:
        metrics[f"gap_count:{record['id']}"] = record["count"]
    for record in duplicates:
        metrics[f"duplicate_count:{record['id']}"] = record["count"]
    return metrics


def evaluate(decl: dict, section_name: str, metrics: dict) -> list[dict]:
    out: list[dict] = []
    for entry in section(decl, section_name):
        metric = str(entry.get("metric") or "")
        measured = metrics.get(metric)
        expected = entry.get("expect")
        met = measured == expected
        out.append(
            {
                "id": str(entry.get("id") or ""),
                "name": str(entry.get("name") or ""),
                "criterion": entry.get("criterion") or "",
                "metric": metric,
                "measured": measured,
                "expect": expected,
                "verdict": "PASS" if met else "FAIL",
            }
        )
    return out


def evaluate_gates(decl: dict, metrics: dict, extra: dict[str, int]) -> list[dict]:
    pool = dict(metrics)
    pool.update(extra)
    out: list[dict] = []
    for entry in section(decl, "gates"):
        failures: list[str] = []
        for metric in as_list(entry.get("metrics")):
            value = pool.get(str(metric))
            if value is None:
                failures.append(f"{metric}: metric not computed")
            elif value:
                failures.append(f"{metric}={value}")
        out.append(
            {
                "id": str(entry.get("id") or ""),
                "name": str(entry.get("name") or ""),
                "blocking": bool(entry.get("blocking")),
                "criterion": entry.get("criterion") or "",
                "metrics": [str(item) for item in as_list(entry.get("metrics"))],
                # Carried from the blueprint because two consumers need it and one of them
                # reads the MODEL rather than the declaration: _observed_verdicts selects
                # working-tree gates from model["gates"], so a field left behind here would
                # silently drop a transitively-dependent gate from the evidence while the
                # other path still recorded it. A fact two readers disagree about is worse
                # than one neither has.
                "working_tree_transitive": bool(entry.get("working_tree_transitive")),
                "failures": failures,
                "verdict": "PASS" if not failures else "FAIL",
            }
        )
    return out


def compliance_findings(decl: dict, gates: list[dict]) -> list[dict]:
    by_id = {gate["id"]: gate for gate in gates}
    ranks = {
        str(entry.get("severity")): int(entry.get("rank") or 0)
        for entry in section(decl, "severities")
    }
    out: list[dict] = []
    for entry in section(decl, "compliance"):
        gate = by_id.get(str(entry.get("gate") or ""))
        if gate is None:
            out.append(
                {
                    "id": str(entry.get("id") or ""),
                    "requirement": entry.get("requirement") or "",
                    "gate": str(entry.get("gate") or ""),
                    "severity": str(entry.get("severity_on_fail") or ""),
                    "rank": ranks.get(str(entry.get("severity_on_fail") or ""), 0),
                    "finding": "the requirement names a gate that is not declared",
                    "remediation": entry.get("remediation") or "",
                }
            )
            continue
        if gate["failures"]:
            out.append(
                {
                    "id": str(entry.get("id") or ""),
                    "requirement": entry.get("requirement") or "",
                    "gate": gate["id"],
                    "severity": str(entry.get("severity_on_fail") or ""),
                    "rank": ranks.get(str(entry.get("severity_on_fail") or ""), 0),
                    "finding": "; ".join(gate["failures"]),
                    "remediation": entry.get("remediation") or "",
                }
            )
    return sorted(out, key=lambda item: (item["rank"], item["id"]))


def run_probes(decl: dict, sub: Substrate) -> list[dict]:
    out: list[dict] = []
    for entry in section(decl, "probes"):
        kind = str(entry.get("kind") or "")
        records = substrate_records(sub, str(entry.get("substrate") or ""), entry.get("pointer"))
        field = str(entry.get("field") or "")
        if kind == "substrate_field_absence":
            present = len(
                [record for record in records if record.get(field) not in (None, "", [], {})]
            )
            headline = f"{present} of {len(records)} records carry the field"
        elif kind == "substrate_field_value_count":
            wanted = str(entry.get("value") or "")
            present = len([record for record in records if str(record.get(field) or "") == wanted])
            headline = f"{present} of {len(records)} records carry the value {wanted!r}"
        else:
            fail_closed(f"{entry.get('id')}: declares an unimplemented probe kind: {kind!r}")
        out.append(
            {
                "id": str(entry.get("id") or ""),
                "kind": kind,
                "purpose": entry.get("purpose") or "",
                "probed": len(records),
                "present": present,
                "headline": headline,
            }
        )
    return out


# ------------------------------------------------------------------------------ model


def derive_identity(decl: dict, units: dict[str, dict]) -> None:
    prefix = str(decl["programme"]["id"])
    for index, key in enumerate(sorted(units), start=1):
        unit = units[key]
        unit["unique_id"] = f"{prefix}-CAP-{index:04d}"
        if not unit["owner"]:
            unit["owner"] = unit["root"] or unit["unit_key"]
        if not unit["program"]:
            unit["program"] = unit["root"] or unit["unit_key"]
        if not unit["lifecycle"]:
            unit["lifecycle"] = str(unit.get("rie_status") or unit.get("corpus_status") or "")
        if not unit["implementation_status"]:
            unit["implementation_status"] = str(unit.get("rie_status") or "")
        unit["is_test_unit"] = bool(unit["location"]) and unit["leaf"] == "tests"


def own_generated_paths(decl: dict) -> set[str]:
    """The artifacts this programme itself rewrites on every run.

    UCOS-CL-015 — the authoritative answer is the generated-artifact registry
    (``00-BOOK/DATA/generated-artifact-registry.json``), not this engine's private reading
    of its own declaration. "This path is generated output" was previously asserted in
    three independent places — here, in ``EXCLUDE_DIR_PREFIXES`` for registration
    eligibility, and in ``.gitignore`` for the version-control boundary — and they drifted:
    UCOS-RECON-C2 records eleven RIE outputs being registered as authored corpus because
    one of those lists had never heard of ``intelligence/``.

    The declaration remains the FALLBACK, so this engine still runs standalone if the
    registry is unreachable. When both are available they must agree, and
    ``reconcile_owner_view`` proves it — a disagreement is a finding, never a silent
    preference for one of the two.
    """
    home = Path(HERE.relative_to(REPO))
    declared = {str(home / str(entry.get("file"))) for entry in section(decl, "outputs")}
    declared.add(str(home / MODEL_FILE))

    root = str(REPO)
    if sys.path[:1] != [root]:
        sys.path.insert(0, root)
    try:
        from platform.repository_intelligence.generated_artifacts import paths_for_owner
    except ImportError:
        return declared
    try:
        registry = paths_for_owner(REPO, "UCOS-RIB-001")
    except (OSError, ValueError, KeyError):
        return declared
    # The registry is upstream and authoritative; the union keeps the engine safe if the
    # registry has not yet caught up with a newly added output, and the reconciliation
    # validation reports that state rather than hiding it.
    return declared | registry


def observed_state(decl: dict, raw: dict) -> dict:
    """Repository state with this programme's own regenerated artifacts subtracted.

    Its own outputs must not appear in its own emitted state. If they did, the artifact
    set would never be idempotent: committing it makes the tree clean, regenerating dirties
    exactly those files again, and each render would disagree with the last over a number
    that describes nothing but the act of rendering. Everything else — an uncommitted
    declaration, engine, README or any file elsewhere in the repository — is retained and
    counted, so the narrowing removes noise without removing dirt.

    Backlog item RB-05 (finding C-5): the per-path LIST is no longer persisted, only the
    counts. That list amplified a scalar condition into ~80 lines of tracked artifact which
    churn with any unrelated repository activity: this model moved +129/-30 -> +137/-30
    across two consecutive audit gate runs solely because an unrelated directory was
    created between them, and the emitted artifact recorded 10 untracked entries while the
    tree already held 11. Persisting a measurement of the working tree's own dirtiness
    inside a TRACKED file is what the repository fixed-point principle forbids -- running
    the gate became a mutation that changed the next measurement. The counts remain, and
    the clean-tree gate and its validation both measure a count, not the list. Every
    offending path stays visible in the gate's stdout report, so nothing is hidden -- only
    the churn surface is removed. Verified before removal: the list was write-only --
    produced here, defaulted in the determinism fixture, read by no code path and rendered
    into no output artifact.
    """
    generated = own_generated_paths(decl)
    entries = [line for line in raw.get("raw_entries", []) if line[3:].strip('"') not in generated]
    state = {key: value for key, value in raw.items() if key != "raw_entries"}
    state.update(
        {
            # UCOS-CL-001 — the ignored-inclusive measurement, resolved against the tracked
            # exclusion register. `dirty_entries` below answers "is the index clean";
            # `contamination` answers "is the repository accounted for". They are different
            # questions, and conflating them is what let an ignore rule clear a gate.
            "contamination": contamination_state(decl),
            "working_tree": "DIRTY" if entries else "CLEAN",
            "dirty_entries": len(entries),
            "modified": len([line for line in entries if line[:2].strip() in {"M", "MM", "AM"}]),
            "deleted": len([line for line in entries if "D" in line[:2]]),
            "untracked": len([line for line in entries if line[:2] == "??"]),
        }
    )
    return state


def build_model(decl: dict, sub: Substrate, repo_input: dict) -> dict:
    repo = observed_state(decl, repo_input) if "raw_entries" in repo_input else repo_input
    units, discovery = discover(decl, sub)
    enrichment = enrich(decl, sub, units)
    measures = measure(decl, sub, units)
    derive_identity(decl, units)
    planes = build_planes(decl, sub, units)
    apply_planes(decl, units, planes)
    transitive_dependents(units)
    duplicates = detect_duplicates(decl, sub, units)
    rules = assign_dispositions(decl, units)
    gaps = detect_gaps(decl, units)
    matrices = build_matrices(decl, units)
    probes = run_probes(decl, sub)
    metrics = compute_metrics(
        decl, sub, units, discovery, planes, duplicates, gaps, matrices, probes, repo
    )
    verifications = evaluate(decl, "verifications", metrics)
    validations = evaluate(decl, "validations", metrics)
    extra = {
        "verifications_failed": len([item for item in verifications if item["verdict"] != "PASS"]),
        "validations_failed": len([item for item in validations if item["verdict"] != "PASS"]),
    }
    gates = evaluate_gates(decl, metrics, extra)
    compliance = compliance_findings(decl, gates)
    queue = build_queue(decl, units)

    disposition_counts: dict[str, int] = {}
    class_counts: dict[str, int] = {}
    for unit in units.values():
        disposition_counts[unit["disposition"]] = disposition_counts.get(unit["disposition"], 0) + 1
        class_counts[unit["unit_class"]] = class_counts.get(unit["unit_class"], 0) + 1

    blocking_failed = [gate["id"] for gate in gates if gate["blocking"] and gate["failures"]]
    gate_open = not blocking_failed
    programme = decl["programme"]
    metrics.update(extra)
    metrics["gate_total"] = len(gates)
    metrics["gates_passed"] = len([gate for gate in gates if not gate["failures"]])
    metrics["blocking_failed"] = blocking_failed
    metrics["disposition_distribution"] = disposition_counts
    metrics["class_distribution"] = class_counts
    metrics["queued_total"] = queue["queued_total"]
    metrics["wave_total"] = len(queue["waves"])
    metrics["max_parallel"] = queue["max_parallel"]
    metrics["substrate_total"] = len(sub.records)
    metrics["substrate_usable"] = len(
        [r for r in sub.records.values() if r["exists"] and r["tracked"] and r["parses"]]
    )
    metrics["matrix_total"] = len(matrices)
    metrics["matrices_bound"] = len([r for r in matrices if r["is_bound"] and r["owner_resolves"]])
    metrics["compliance_findings"] = len(compliance)

    model = {
        "programme": programme,
        "tracking": section(decl, "tracking"),
        "repository": repo,
        "substrate": [sub.records[key] for key in sorted(sub.records)],
        "discovery": discovery,
        "enrichment": enrichment,
        "measures": measures,
        "units": [units[key] for key in sorted(units)],
        "planes": [
            {key: value for key, value in plane.items() if key not in ("adjacency", "inbound")}
            for plane in planes
        ],
        "duplicates": duplicates,
        "gaps": gaps,
        "dispositions": section(decl, "dispositions"),
        "disposition_rules": rules,
        "cycle_classes": section(decl, "cycle_classes"),
        "matrices": matrices,
        "verifications": verifications,
        "validations": validations,
        "gates": gates,
        "compliance": compliance,
        "severities": section(decl, "severities"),
        "queue": queue,
        "probes": probes,
        "non_derivable": section(decl, "non_derivable"),
        "work_packages": section(decl, "work_packages"),
        "references": section(decl, "references"),
        "metrics": metrics,
        "gate": "OPEN" if gate_open else "CLOSED",
        "determination": (
            programme["determination_pass"] if gate_open else programme["determination_fail"]
        ),
        "gate_exit": 0 if gate_open else 1,
    }
    model["seal_sha256"] = digest(seal_payload(model))
    # (the seal is re-derived from the CANONICAL structures in canonical_model — see
    #  seal_payload, which is the single definition of what a seal covers.)
    return model


# --------------------------------------------------------------------------- rendering


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
                ["MISSION / PROMPT", f"`{programme['mission']}` · `{programme['prompt']}`"],
                ["AUTHORITY", f"**{programme['authority']}**"],
                ["GOVERNING INSTRUMENT", f"`{programme['governing_instrument']}`"],
                ["OPERATIONAL HOME", f"`{programme['operational_home']}`"],
                ["REPOSITORY ANCHOR", repo["anchor"]],
                ["WORKING TREE", _working_tree_row(repo)],
                ["UNITS DISCOVERED", str(m["unit_total"])],
                ["SUBSTRATE USABLE", f"{m['substrate_usable']}/{m['substrate_total']}"],
                ["GATES", f"{m['gates_passed']}/{m['gate_total']}"],
                ["DETERMINATION", f"**{model['determination']}**"],
                [
                    programme["gate_name"].upper(),
                    f"**{model['gate']}** (`{programme['gate_clause']}`)",
                ],
                ["SEAL (sha256)", f"`{model['seal_sha256']}`"],
                ["GENERATED BY", "`rib_engine.py` — regenerated, never hand-authored"],
            ],
        )
        + f"\n> {purpose}\n\n"
        + f"> **DISCLOSURE.** {programme['disclosure']}\n\n---\n\n"
    )


FOOTER = (
    "\n---\n\n*This blueprint is DERIVED TRUTH. It creates no authority, allocates no permanent "
    "corpus identity, ratifies nothing, freezes nothing and supersedes no governing instrument. "
    "Every matrix marked BOUND is a pointer to the owner that already holds it and carries no row "
    "of its own; every matrix marked DERIVED is computed from declared substrate. Every capability "
    "disposition is the output of exactly one ordered rule, and the rule is named beside it. Where "
    "a fact could not be honestly derived, the absence is declared and counted rather than filled "
    "in. Where this document conflicts with a higher frozen or governing instrument, the higher "
    "instrument governs.*\n"
)

UNIT_HEADERS = [
    "ID",
    "Capability",
    "Class",
    "Location",
    "Src",
    "Dep",
    "Cons",
    "Iface",
    "Reg",
    "Tests",
    "Cov",
    "Status",
    "Disposition",
    "Rule",
]


def unit_rows(units: list[dict]) -> list[list[str]]:
    return [
        [
            f"`{unit['unique_id']}`",
            f"`{short(unit['canonical_name'], 44)}`",
            unit["unit_class"] or "—",
            f"`{short(unit['location'], 40)}`" if unit["location"] else "—",
            str(unit["source_files"]),
            str(unit["dependencies"]),
            str(unit["consumers"]),
            str(unit["interfaces"]),
            str(unit["registered_artifacts"]),
            str(unit["unit_tests"]),
            "YES" if unit["in_coverage_scope"] else "no",
            short(unit["implementation_status"] or unit["lifecycle"] or "—", 18),
            f"**{unit['disposition']}**",
            f"`{unit['disposition_rule']}`",
        ]
        for unit in units
    ]


def verdict_rows(items: list[dict]) -> list[list[str]]:
    return [
        [
            f"`{item['id']}`",
            item["name"],
            item["criterion"],
            f"`{item['metric']}`",
            f"{item['measured']} (expected {item['expect']})",
            f"**{item['verdict']}**",
        ]
        for item in items
    ]


def render(decl: dict, model: dict) -> dict[str, str]:
    spec = section(decl, "outputs")
    files = [str(entry.get("file")) for entry in spec]
    titles = [str(entry.get("title")) for entry in spec]
    purposes = [str(entry.get("purpose")) for entry in spec]
    m = model["metrics"]
    units = model["units"]
    by_key = {unit["unit_key"]: unit for unit in units}
    out: dict[str, str] = {}

    def page(index: int) -> str:
        return header(titles[index], decl, model, purposes[index])

    # ---- 00 dashboard
    out[files[0]] = (
        page(0)
        + "## Determination\n\n"
        + table(
            ["Dimension", "Value"],
            [
                ["Units discovered", str(m["unit_total"])],
                [
                    "Discovery sources",
                    f"{len(model['discovery'])} (empty: {m['discovery_sources_empty']})",
                ],
                ["Substrate usable", f"{m['substrate_usable']}/{m['substrate_total']}"],
                [
                    "Matrices bound to an existing owner",
                    f"{m['matrices_bound']}/{m['matrix_total']}",
                ],
                ["Matrices unbound", str(m["matrices_unbound"])],
                ["Verification obligations failed", str(m["verifications_failed"])],
                ["Validation obligations failed", str(m["validations_failed"])],
                ["Duplicate findings", str(m["duplicate_findings"])],
                ["Gap findings", str(m["gap_findings"])],
                ["Architectural cycles", str(m["architectural_cycles"])],
                ["Benign cycles (declared class)", str(m["benign_cycles"])],
                ["Orphan units", str(m["orphan_units"])],
                ["Queued units", f"{m['queued_total']} in {m['wave_total']} wave(s)"],
                ["Maximum parallelism", str(m["max_parallel"])],
                ["Compliance findings", str(m["compliance_findings"])],
                ["Gates passed", f"{m['gates_passed']}/{m['gate_total']}"],
                ["Blocking gate failures", ", ".join(m["blocking_failed"]) or "none"],
                ["Determination", f"**{model['determination']}**"],
                ["Gate", f"**{model['gate']}**"],
            ],
        )
        + "\n## Quality gates\n\n"
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
        + "\n## Disposition distribution\n\n"
        + table(
            ["Disposition", "Units", "Definition"],
            [
                [
                    f"**{entry['disposition']}**",
                    str(m["disposition_distribution"].get(str(entry["disposition"]), 0)),
                    entry["definition"],
                ]
                for entry in model["dispositions"]
            ],
        )
        + "\n## Unit classes discovered\n\n"
        + table(
            ["Class", "Units"],
            [[key or "—", str(value)] for key, value in sorted(m["class_distribution"].items())],
        )
        + "\n## Immutable tracking identities\n\n"
        + table(
            ["Tracking", "Family", "Value", "Allocation", "Purpose"],
            [
                [
                    f"`{entry['id']}`",
                    entry["family"],
                    f"`{entry['value']}`",
                    entry["allocation"],
                    entry["purpose"],
                ]
                for entry in model["tracking"]
            ],
        )
        + f"\n- **Execution identity** — `{model['seal_sha256']}`\n"
        + f"- **Repository anchor** — {model['repository']['anchor']}\n"
        + FOOTER
    )

    # ---- 01 inventory
    out[files[1]] = (
        page(1)
        + "## Discovery sources — nothing enumerated, everything discovered\n\n"
        + table(
            ["Source", "Kind", "Class", "Selector", "Probed", "Units", "Purpose"],
            [
                [
                    f"`{item['id']}`",
                    f"`{item['kind']}`",
                    item["class"] or "—",
                    f"`{short(item['selector'], 34)}`",
                    str(item["probed"]),
                    str(item["units"]),
                    item["purpose"],
                ]
                for item in model["discovery"]
            ],
        )
        + "\n## Substrate\n\n"
        + table(
            ["Substrate", "Path", "Kind", "Tracked", "Parses", "Pointers", "Records", "Content"],
            [
                [
                    f"`{record['id']}`",
                    f"`{record['path']}`",
                    record["kind"],
                    "YES" if record["tracked"] else "**NO**",
                    "YES" if record["parses"] else "**NO**",
                    f"{len(record['pointers_resolved'])}/{len(record['pointers'])}",
                    str(record["records"]),
                    f"`{record['content_sha256'][:12]}`",
                ]
                for record in model["substrate"]
            ],
        )
        + "\n## Enrichment\n\n"
        + table(
            ["Enrichment", "Records", "Matched", "Purpose"],
            [
                [f"`{item['id']}`", str(item["records"]), str(item["matched"]), item["purpose"]]
                for item in model["enrichment"]
            ],
        )
        + "\n## Measures applied to every unit\n\n"
        + table(
            ["Measure", "Kind", "Field", "Units with a value", "Total", "Purpose"],
            [
                [
                    f"`{item['id']}`",
                    f"`{item['kind']}`",
                    f"`{item['field']}`",
                    str(item["units_with_value"]),
                    str(item["total"]),
                    item["purpose"],
                ]
                for item in model["measures"]
            ],
        )
        + "\n## Repository reality at the computed anchor\n\n"
        + table(
            ["Dimension", "Value"],
            [
                ["Repository anchor", model["repository"]["anchor"]],
                ["Detached", "YES" if model["repository"]["detached"] else "no"],
                ["Working tree", model["repository"]["working_tree"]],
                ["Dirty entries", str(model["repository"]["dirty_entries"])],
                [
                    "Own regenerated artifacts",
                    "excluded from the count above — they are the deterministic product of "
                    "the command being gated",
                ],
                ["Modified", str(model["repository"]["modified"])],
                ["Deleted", str(model["repository"]["deleted"])],
                ["Untracked", str(model["repository"]["untracked"])],
                ["Merge conflicts", str(model["repository"]["conflicts"])],
                [
                    "Interrupted operations",
                    ", ".join(model["repository"]["interrupted_operations"]) or "none",
                ],
                ["Broken symlinks", str(len(model["repository"]["broken_symlinks"]))],
                ["Version-controlled files", str(model["repository"]["tracked_files"])],
            ],
        )
        + FOOTER
    )

    # ---- 02 capability graph
    out[files[2]] = (
        page(2)
        + f"## Every discovered capability unit ({len(units)})\n\n"
        + table(UNIT_HEADERS, unit_rows(units))
        + "\n## Column derivation\n\n"
        + table(
            ["Column", "Derived from"],
            [
                [
                    "ID",
                    "allocated deterministically over the sorted unit key set — stable "
                    "for an unchanged repository",
                ],
                ["Class", "the declared class of the discovery source that produced the unit"],
                [
                    "Src / Reg / Tests",
                    "counted version-controlled paths and registered artifacts homed in the unit",
                ],
                ["Dep / Cons", "measured edges in every plane the unit participates in"],
                [
                    "Iface",
                    "the declared console entry points whose target resolves inside the unit",
                ],
                ["Cov", "membership of the declared coverage scope"],
                ["Disposition / Rule", "the first matching ordered rule — exactly one, always one"],
            ],
        )
        + FOOTER
    )

    # ---- 03 owner matrix
    out[files[3]] = (
        page(3)
        + "## One owner per capability\n\n"
        + table(
            ["ID", "Capability", "Owner", "Programme", "Phase", "Governing instrument"],
            [
                [
                    f"`{unit['unique_id']}`",
                    f"`{short(unit['canonical_name'], 44)}`",
                    f"`{unit['owner']}`",
                    f"`{unit['program']}`",
                    unit["phase"] or "**not derivable**",
                    f"`{short(unit.get('uei_instrument') or '', 42)}`"
                    if unit.get("uei_instrument")
                    else "—",
                ]
                for unit in units
            ],
        )
        + "\n## Ownership collisions\n\n"
        + table(
            ["Dimension", "Value"],
            [
                ["Units", str(m["unit_total"])],
                ["Units claiming a location claimed by another unit", str(m["owner_collisions"])],
                ["Units with no owner", str(len([u for u in units if not u["owner"]]))],
                ["Units with no programme", str(m["units_without_program"])],
            ]
            + [
                [
                    f"Units with no derivable `{key.split(':', 1)[1]}`",
                    f"{value} — of which {m.get('absent_unbounded:' + key.split(':', 1)[1], 0)} "
                    "not covered by a registered refusal",
                ]
                for key, value in sorted(m.items())
                if key.startswith("absent:")
            ],
        )
        + "\n> Phase is reported as **not derivable** wherever no substrate binds the unit to a "
        + "ratified programme phase. The absence is registered, counted and owned rather than "
        + "invented — see the non-derivable register below.\n\n"
        + table(
            ["Fact", "Why it cannot be derived", "Evidence class required", "Owner"],
            [
                [
                    entry["fact"],
                    entry["reason"],
                    entry["required_evidence_class"],
                    f"`{entry['owner']}`",
                ]
                for entry in model["non_derivable"]
            ],
        )
        + "\n### Counted probes behind those refusals\n\n"
        + table(
            ["Probe", "Probed", "Present", "Result"],
            [
                [f"`{p['id']}`", str(p["probed"]), str(p["present"]), p["headline"]]
                for p in model["probes"]
            ],
        )
        + FOOTER
    )

    # ---- 04 the blueprint itself: sixteen matrices
    body = page(4) + "## The sixteen matrices\n\n"
    body += table(
        ["#", "Matrix", "Name", "Mode", "Canonical owner", "Resolves", "Rows here"],
        [
            [
                str(record["index"]),
                f"`{record['id']}`",
                record["name"],
                f"**{record['mode']}**",
                f"`{short(record['canonical_owner'], 46)}`" if record["canonical_owner"] else "—",
                "OK"
                if record["owner_resolves"]
                else ("n/a" if not record["canonical_owner"] else "**MISSING**"),
                str(record["rows"]),
            ]
            for record in sorted(model["matrices"], key=lambda item: item["index"])
        ],
    )
    body += (
        "\n> A matrix marked **BOUND** is discharged by the owner that already holds it: this "
        "blueprint emits the pointer and no rows, which is what makes the binding a reuse rather "
        "than a second truth. A matrix marked **DERIVED** is computed here because no canonical "
        "owner holds it in machine-readable form.\n\n"
    )
    for record in sorted(model["matrices"], key=lambda item: item["index"]):
        body += f"### {record['index']}. {record['name']} — `{record['id']}`\n\n"
        body += f"{record['subject']}\n\n"
        if record["is_bound"]:
            body += (
                f"- **Mode** — BOUND\n- **Canonical owner** — `{record['canonical_owner']}`\n"
                f"- **Owner resolves** — {'YES' if record['owner_resolves'] else '**NO**'}\n"
                "- **Rows emitted here** — 0 (reuse, not restatement)\n\n"
            )
            continue
        body += (
            "- **Mode** — DERIVED\n- **Nearest existing owner** — "
            + (
                f"`{record['canonical_owner']}` — {record['owner_form']}"
                if record["canonical_owner"]
                else "none located"
            )
            + f"\n- **Columns** — {', '.join(f'`{c}`' for c in record['columns'])}\n\n"
        )
        columns = record["columns"]
        if columns and columns[0] == "unique_id":
            body += table(
                [c.replace("_", " ") for c in columns],
                [[short(unit.get(c, ""), 44) for c in columns] for unit in units],
            )
        else:
            body += render_special_matrix(model, record)
        body += "\n"
    out[files[4]] = body + FOOTER

    # ---- 05 dependency graph
    body = page(5)
    for plane in model["planes"]:
        body += (
            f"## `{plane['id']}` — {plane['purpose']}\n\n"
            + table(
                ["Dimension", "Value"],
                [
                    ["Kind", f"`{plane['kind']}`"],
                    ["Nodes", str(plane["nodes"])],
                    ["Edges", str(plane["edges"])],
                    ["Unresolved edges", str(plane["unresolved_edges"])],
                    ["Cycles", str(len(plane["cycles"]))],
                    ["Cycles of a non-benign class", str(len(plane["architectural_cycles"]))],
                ],
            )
            + "\n"
        )
        if plane["cycles"]:
            body += "### Cycles, classified\n\n" + table(
                ["Class", "Benign", "Cycle", "Units"],
                [
                    [
                        f"`{item['class']}`",
                        "YES" if item["benign"] else "**NO**",
                        " → ".join(f"`{short(node, 34)}`" for node in item["cycle"]),
                        str(len(item["units"])),
                    ]
                    for item in plane["cycles"]
                ],
            )
            cycle_edges = {
                f"{item['cycle'][index]} -> {item['cycle'][index + 1]}"
                for item in plane["architectural_cycles"]
                for index in range(len(item["cycle"]) - 1)
            }
            named = {key: value for key, value in plane["edge_sites"].items() if key in cycle_edges}
            if named:
                body += "\n### The mediating modules of each non-benign cycle\n\n" + table(
                    ["Edge", "Import site(s)"],
                    [
                        [f"`{key}`", ", ".join(f"`{item}`" for item in value)]
                        for key, value in sorted(named.items())
                    ],
                )
            body += "\n"
    body += "## Declared cycle classes\n\n" + table(
        ["Class", "Benign", "Definition", "Evidence"],
        [
            [
                f"`{entry['id']}`",
                "YES" if entry.get("benign") else "**NO**",
                entry.get("definition") or "",
                entry.get("evidence") or "",
            ]
            for entry in model["cycle_classes"]
        ],
    )
    body += "\n## Dependency closure\n\n" + table(
        ["Dimension", "Value"],
        [
            ["Unresolved dependency edges (all planes)", str(m["unresolved_dependency_edges"])],
            ["Closure", "**PASS**" if not m["unresolved_dependency_edges"] else "**FAIL**"],
        ],
    )
    out[files[5]] = body + FOOTER

    # ---- 06 gap analysis
    body = (
        page(6)
        + "## Gap register\n\n"
        + table(
            ["Gap", "Class", "Subject", "Restricted to", "Count"],
            [
                [
                    f"`{entry['id']}`",
                    entry["class"],
                    entry["subject"],
                    entry["restrict_class"] or "all classes",
                    str(entry["count"]),
                ]
                for entry in model["gaps"]
            ],
        )
    )
    for entry in model["gaps"]:
        if not entry["count"]:
            continue
        body += (
            f"\n### {entry['id']} — {entry['class']} ({entry['count']})\n\n"
            + f"{entry['subject']}\n\n"
            + table(
                ["ID", "Capability", "Class", "Location", "Disposition"],
                [
                    [
                        f"`{by_key[key]['unique_id']}`",
                        f"`{short(key, 44)}`",
                        by_key[key]["unit_class"] or "—",
                        f"`{short(by_key[key]['location'], 40)}`"
                        if by_key[key]["location"]
                        else "—",
                        f"**{by_key[key]['disposition']}**",
                    ]
                    for key in entry["members"]
                    if key in by_key
                ],
            )
        )
    out[files[6]] = body + FOOTER

    # ---- 07 duplicate analysis
    body = (
        page(7)
        + "## Duplicate register\n\n"
        + table(
            ["Duplicate", "Class", "Rule", "Subject", "Findings"],
            [
                [
                    f"`{entry['id']}`",
                    entry["class"],
                    f"`{entry['rule']}`",
                    entry["subject"],
                    str(entry["count"]),
                ]
                for entry in model["duplicates"]
            ],
        )
    )
    for entry in model["duplicates"]:
        if not entry["count"]:
            continue
        body += f"\n### {entry['id']} — {entry['class']} ({entry['count']})\n\n" + table(
            ["Colliding on", "Members"],
            [
                [
                    f"`{short(item['subject'], 60)}`",
                    ", ".join(f"`{short(x, 40)}`" for x in item["members"]) or "—",
                ]
                for item in entry["findings"][:60]
            ],
        )
        if entry["count"] > 60:
            body += f"\n> {entry['count'] - 60} further finding(s) recorded in `{MODEL_FILE}`.\n"
    out[files[7]] = body + FOOTER

    # ---- 08 reuse analysis
    reuse_flags = {
        str(entry["disposition"]): bool(entry.get("is_reuse")) for entry in model["dispositions"]
    }
    reused = [unit for unit in units if reuse_flags.get(unit["disposition"], False)]
    out[files[8]] = (
        page(8)
        + "## What is consumed rather than rebuilt\n\n"
        + table(
            ["Dimension", "Value"],
            [
                ["Units disposed to a reuse outcome", f"{len(reused)}/{len(units)}"],
                [
                    "Reuse dispositions",
                    ", ".join(
                        f"**{key}**" for key, value in sorted(reuse_flags.items()) if value and key
                    ),
                ],
                [
                    "Matrices discharged by an existing owner",
                    f"{m['matrices_bound']}/{m['matrix_total']}",
                ],
                [
                    "Capability records bound from the canonical catalogue",
                    str(m["catalogue_records"]),
                ],
            ],
        )
        + "\n## Reused units\n\n"
        + table(
            ["ID", "Capability", "Disposition", "Recorded reuse", "Authority", "Rule"],
            [
                [
                    f"`{unit['unique_id']}`",
                    f"`{short(unit['canonical_name'], 44)}`",
                    f"**{unit['disposition']}**",
                    f"`{unit.get('rie_reuse') or '—'}`",
                    short(unit.get("rie_authority") or "—", 24),
                    f"`{unit['disposition_rule']}`",
                ]
                for unit in reused
            ],
        )
        + FOOTER
    )

    # ---- 09 extension analysis
    change_flags = {
        str(entry["disposition"]): bool(entry.get("is_change")) for entry in model["dispositions"]
    }
    changed = [unit for unit in units if change_flags.get(unit["disposition"], False)]
    out[files[9]] = (
        page(9)
        + "## What is changed rather than replaced\n\n"
        + table(
            ["Disposition", "Units", "Definition", "Adds surface", "Removes surface"],
            [
                [
                    f"**{entry['disposition']}**",
                    str(m["disposition_distribution"].get(str(entry["disposition"]), 0)),
                    entry["definition"],
                    "YES" if entry.get("is_change") else "no",
                    "YES" if entry.get("is_removal") else "no",
                ]
                for entry in model["dispositions"]
                if entry.get("is_change")
            ],
        )
        + "\n## Units carrying a change disposition\n\n"
        + table(
            ["ID", "Capability", "Disposition", "Why", "Dependents", "Wave"],
            [
                [
                    f"`{unit['unique_id']}`",
                    f"`{short(unit['canonical_name'], 40)}`",
                    f"**{unit['disposition']}**",
                    short(unit["disposition_reason"], 78),
                    str(unit["dependents"]),
                    str(wave_of(model, unit["unit_key"])),
                ]
                for unit in changed
            ],
        )
        + FOOTER
    )

    # ---- 10 implementation queue
    queue = model["queue"]
    out[files[10]] = (
        page(10)
        + "## Queue shape\n\n"
        + table(
            ["Dimension", "Value"],
            [
                ["Units consuming the queue", str(queue["queued_total"])],
                ["Waves", str(len(queue["waves"]))],
                ["Maximum parallelism", str(queue["max_parallel"])],
                [
                    "Sequencing",
                    "computed by dependency-safe topological banding — never hand-ordered",
                ],
            ],
        )
        + "\n## Waves — every unit in a wave may execute in parallel\n\n"
        + table(
            ["Wave", "Parallel", "Units", "Blocked by (earlier waves)"],
            [
                [
                    str(wave["wave"]),
                    str(wave["parallel"]),
                    ", ".join(f"`{short(key, 34)}`" for key in wave["units"]),
                    ", ".join(f"`{short(key, 28)}`" for key in wave["blocked_by"]) or "—",
                ]
                for wave in queue["waves"]
            ],
        )
        + "\n## Critical path — the units with the widest transitive dependent set\n\n"
        + table(
            ["#", "Capability", "Disposition", "Dependents", "Wave"],
            [
                [
                    str(index + 1),
                    f"`{short(key, 44)}`",
                    f"**{by_key[key]['disposition']}**",
                    str(by_key[key]["dependents"]),
                    str(wave_of(model, key)),
                ]
                for index, key in enumerate(queue["critical_path"])
                if key in by_key
            ],
        )
        + "\n## Priority order\n\n"
        + table(
            ["Rank", "Capability", "Disposition", "Wave", "Dependents"],
            [
                [
                    str(item["rank"]),
                    f"`{short(item['unit_key'], 44)}`",
                    f"**{item['disposition']}**",
                    str(item["wave"]),
                    str(item["dependents"]),
                ]
                for item in queue["priority"]
            ],
        )
        + FOOTER
    )

    # ---- 11 verification report
    out[files[11]] = (
        page(11)
        + "## Verification obligations\n\n"
        + table(
            ["Obligation", "Name", "Criterion", "Metric", "Measured", "Verdict"],
            verdict_rows(model["verifications"]),
        )
        + "\n## Verification evidence\n\n"
        + table(
            ["Evidence", "Value"],
            [
                ["Units discovered", str(m["unit_total"])],
                [
                    "Units with exactly one disposition",
                    str(m["unit_total"] - m["units_without_disposition"]),
                ],
                [
                    "Dependency edges measured",
                    str(sum(plane["edges"] for plane in model["planes"])),
                ],
                ["Unresolved dependency edges", str(m["unresolved_dependency_edges"])],
                ["Registered artifacts probed", str(m["catalogue_records"])],
                ["Dead registry entries", str(m["dead_registry_entries"])],
                [
                    "Dead engines (no declared entry point names them)",
                    ", ".join(
                        f"`{key}`"
                        for record in model["gaps"]
                        if record["id"] == dead_engine_gap(model)
                        for key in record["members"]
                    )
                    or "0",
                ],
                ["Dead interfaces", ", ".join(m["dead_interface_members"]) or "0"],
                ["Orphan units", ", ".join(f"`{key}`" for key in m["orphan_members"]) or "0"],
                ["Evidence index", f"`evidence/{EVIDENCE_INDEX}`"],
                ["Seal", f"`{model['seal_sha256']}`"],
            ],
        )
        + FOOTER
    )

    # ---- 12 validation report
    out[files[12]] = (
        page(12)
        + "## Validation obligations\n\n"
        + table(
            ["Obligation", "Name", "Criterion", "Metric", "Measured", "Verdict"],
            verdict_rows(model["validations"]),
        )
        + "\n## Rule totality — the property that makes the disposition set trustworthy\n\n"
        + table(
            ["Rule", "Disposition", "Clauses", "Units matched", "Because"],
            [
                [
                    f"`{rule['id']}`",
                    f"**{rule['disposition']}**",
                    str(rule["clauses"]) if rule["clauses"] else "0 (catch-all)",
                    str(rule["units"]),
                    short(rule["because"], 88),
                ]
                for rule in model["disposition_rules"]
            ],
        )
        + "\n> The final rule carries zero clauses, so the rule set is **total**: every unit "
        + "matches at least one rule, the first match wins, and no unit can carry two "
        + "dispositions or none.\n"
        + FOOTER
    )

    # ---- 13 certification report
    out[files[13]] = (
        page(13)
        + "## The twelve quality gates\n\n"
        + table(
            ["Gate", "Name", "Blocking", "Criterion", "Metrics", "Verdict"],
            [
                [
                    f"`{gate['id']}`",
                    gate["name"],
                    "YES" if gate["blocking"] else "advisory",
                    gate["criterion"],
                    ", ".join(f"`{item}`" for item in gate["metrics"]),
                    f"**{gate['verdict']}**"
                    + ("" if not gate["failures"] else " — " + "; ".join(gate["failures"])),
                ]
                for gate in model["gates"]
            ],
        )
        + "\n## Compliance findings, classified\n\n"
        + table(
            ["Severity", "Finding", "Requirement", "Gate", "Remediation"],
            [
                [
                    f"**{item['severity']}**",
                    item["finding"],
                    item["requirement"],
                    f"`{item['gate']}`",
                    item["remediation"],
                ]
                for item in model["compliance"]
            ],
        )
        + "\n## Severity scale\n\n"
        + table(
            ["Severity", "Rank", "Definition"],
            [
                [f"**{entry['severity']}**", str(entry["rank"]), entry["definition"]]
                for entry in model["severities"]
            ],
        )
        + "\n## Certification determination\n\n"
        + table(
            ["Criterion", "Value", "Verdict"],
            [
                [
                    "Repository clean",
                    f"{model['repository']['working_tree']} — "
                    f"{m['dirty_entries_outside_generated']} entr(y/ies), excluding this "
                    "programme's own regenerated artifacts",
                    "PASS" if not m["dirty_entries_outside_generated"] else "**FAIL**",
                ],
                [
                    "Verification",
                    f"{len(model['verifications']) - m['verifications_failed']}"
                    f"/{len(model['verifications'])}",
                    "PASS" if not m["verifications_failed"] else "**FAIL**",
                ],
                [
                    "Validation",
                    f"{len(model['validations']) - m['validations_failed']}"
                    f"/{len(model['validations'])}",
                    "PASS" if not m["validations_failed"] else "**FAIL**",
                ],
                [
                    "Dependency closure",
                    str(m["unresolved_dependency_edges"]),
                    "PASS" if not m["unresolved_dependency_edges"] else "**FAIL**",
                ],
                [
                    "Capability coverage",
                    f"{m['unresolved_catalogue_records']} unresolved · "
                    f"{m['uncatalogued_units']} uncatalogued",
                    "PASS"
                    if not (m["unresolved_catalogue_records"] or m["uncatalogued_units"])
                    else "**FAIL**",
                ],
                [
                    "Certification",
                    f"{m['certification_domains_failed']} domain(s) failed",
                    "PASS"
                    if not (m["certification_domains_failed"] or m["certification_verdict_absent"])
                    else "**FAIL**",
                ],
                ["Determination", model["determination"], f"**{model['gate']}**"],
            ],
        )
        + FOOTER
    )

    # ---- 14 readiness report
    blocking = [gate for gate in model["gates"] if gate["blocking"] and gate["failures"]]
    out[files[14]] = (
        page(14)
        + "## Verdict\n\n"
        + f"# {model['determination']}\n\n"
        + (
            "Every blocking gate passed. The blueprint is the implementation contract for all "
            "future work, and the queue in output 10 is the authorized order.\n\n"
            if not blocking
            else "The blueprint is complete and every finding below is measured, but the "
            "repository may **not** proceed to certification while a blocking gate is failing. "
            "Each blocker names the metric that produced it and the owner of the unblocking "
            "act.\n\n"
        )
        + "## Blocking gates\n\n"
        + table(
            ["Gate", "Name", "Measured failure", "Requirement it violates", "Remediation"],
            [
                [
                    f"`{gate['id']}`",
                    gate["name"],
                    "; ".join(gate["failures"]),
                    "; ".join(
                        item["requirement"]
                        for item in model["compliance"]
                        if item["gate"] == gate["id"]
                    )
                    or "—",
                    "; ".join(
                        item["remediation"]
                        for item in model["compliance"]
                        if item["gate"] == gate["id"]
                    )
                    or "—",
                ]
                for gate in blocking
            ],
        )
        + "\n## Mission success criteria\n\n"
        + table(
            ["Criterion", "Measured", "Verdict"],
            [
                [
                    "Repository is version-control clean",
                    f"{m['dirty_entries_outside_generated']} dirty entr(y/ies), excluding "
                    "this programme's own regenerated artifacts",
                    "PASS" if not m["dirty_entries_outside_generated"] else "**FAIL**",
                ],
                [
                    "Verification PASS",
                    f"{m['verifications_failed']} failed",
                    "PASS" if not m["verifications_failed"] else "**FAIL**",
                ],
                [
                    "Validation PASS",
                    f"{m['validations_failed']} failed",
                    "PASS" if not m["validations_failed"] else "**FAIL**",
                ],
                [
                    "Certification PASS",
                    f"{len(blocking)} blocking gate(s) failing",
                    "PASS" if not blocking else "**FAIL**",
                ],
                [
                    "Repository Truth synchronized",
                    model["repository"]["anchor"],
                    "PASS",
                ],
                [
                    "Canonical blueprint generated",
                    f"{len(model['matrices'])} matrices, {len(files)} outputs",
                    "PASS",
                ],
                [
                    "Zero duplicate capability ownership",
                    f"{m['duplicate_findings']} duplicate finding(s)",
                    "PASS" if not m["duplicate_findings"] else "**FAIL**",
                ],
                [
                    "Zero unresolved dependency",
                    str(m["unresolved_dependency_edges"]),
                    "PASS" if not m["unresolved_dependency_edges"] else "**FAIL**",
                ],
                [
                    "Zero orphan implementation",
                    str(m["orphan_units"]),
                    "PASS" if not m["orphan_units"] else "**FAIL**",
                ],
                [
                    "Dependency-safe queue generated",
                    f"{m['queued_total']} units in {m['wave_total']} wave(s)",
                    "PASS" if m["wave_total"] or not m["queued_total"] else "**FAIL**",
                ],
            ],
        )
        + "\n## Work packages\n\n"
        + table(
            ["Work package", "Title", "Owner", "Route", "Authorization", "Acceptance"],
            [
                [
                    f"`{entry['id']}`",
                    entry["title"],
                    f"`{entry['owner']}`",
                    f"`{entry['route']}`",
                    "required" if entry["authorization_required"] else "not required",
                    entry["acceptance"],
                ]
                for entry in model["work_packages"]
            ],
        )
        + "\n## Continuation package\n\n"
        + table(
            ["Element", "Value"],
            [
                ["Anchor", model["repository"]["anchor"]],
                ["Regeneration route", f"`{model['work_packages'][0]['route']}`"],
                [
                    "Completed work",
                    f"{m['unit_total']} unit(s) discovered from "
                    f"{len(model['discovery'])} source(s), each carrying exactly one "
                    f"disposition; {m['matrix_total']} matrices bound or derived; "
                    f"{m['gate_total']} gates evaluated",
                ],
                [
                    "Remaining work",
                    f"{m['queued_total']} unit(s) queued across {m['wave_total']} "
                    f"wave(s); {len(blocking)} blocking gate(s) to clear",
                ],
                [
                    "Open refusals",
                    ", ".join(f"`{entry['id']}`" for entry in model["non_derivable"]) or "none",
                ],
                [
                    "Architectural decisions",
                    "Reuse-first and zero-duplication: no capability catalogue, dependency "
                    "graph, registry, queue or certification authority was created; every "
                    "matrix is a pointer, a derivation over declared substrate, or a "
                    "counted absence",
                ],
                ["Seal", f"`{model['seal_sha256']}`"],
            ],
        )
        + "\n## Bound canonical references\n\n"
        + table(
            ["Reference", "Path", "Resolves", "Purpose"],
            [
                [
                    f"`{entry['id']}`",
                    f"`{entry['path']}`",
                    "OK" if resolve_reference(str(entry["path"])) is not None else "**MISSING**",
                    entry["purpose"],
                ]
                for entry in model["references"]
            ],
        )
        + FOOTER
    )
    return out


def dead_engine_gap(model: dict) -> str:
    """The declared gap whose members are programmes no entry point names."""
    for record in model["gaps"]:
        for item in model["verifications"]:
            if item["metric"] == f"gap_count:{record['id']}":
                return record["id"]
    return ""


def wave_of(model: dict, key: str) -> int:
    for wave in model["queue"]["waves"]:
        if key in wave["units"]:
            return wave["wave"]
    return 0


def render_special_matrix(model: dict, record: dict) -> str:
    """Render a derived matrix whose rows are not per-unit."""
    columns = record["columns"]
    m = model["metrics"]
    if columns[:2] == ["id", "severity"]:
        return table(
            ["ID", "Severity", "Finding", "Remediation"],
            [
                [f"`{item['id']}`", f"**{item['severity']}**", item["finding"], item["remediation"]]
                for item in model["compliance"]
            ],
        )
    if columns[:1] == ["disposition"]:
        return table(
            ["Disposition", "Units", "What it delivers"],
            [
                [
                    f"**{entry['disposition']}**",
                    str(m["disposition_distribution"].get(str(entry["disposition"]), 0)),
                    entry["definition"],
                ]
                for entry in model["dispositions"]
            ],
        ) + (
            "\n> Benefit is reported as the coverage each disposition achieves. A monetary or "
            "user-facing benefit figure is declared non-derivable and counted, not estimated.\n"
        )
    if columns[:1] == ["wave"]:
        return table(
            ["Wave", "Units", "Parallel", "Blocked by"],
            [
                [
                    str(wave["wave"]),
                    ", ".join(f"`{short(key, 30)}`" for key in wave["units"]),
                    str(wave["parallel"]),
                    ", ".join(f"`{short(key, 24)}`" for key in wave["blocked_by"]) or "—",
                ]
                for wave in model["queue"]["waves"]
            ],
        )
    if columns[:1] == ["id"]:
        return table(
            ["ID", "Name", "Verdict"],
            [
                [f"`{item['id']}`", item["name"], f"**{item['verdict']}**"]
                for item in model["validations"]
            ],
        )
    return table(
        ["ID", "Capability"] + [c.replace("_", " ") for c in columns[2:]],
        [
            [f"`{unit['unique_id']}`", f"`{short(unit['canonical_name'], 40)}`"]
            + [short(unit.get(c, ""), 30) for c in columns[2:]]
            for unit in model["units"]
        ],
    )


# ------------------------------------------------------------------------ self-guards


def check_declaration(decl: dict, sub: Substrate | None = None) -> list[str]:
    """Declaration integrity. An unusable declaration may assert no verdict."""
    findings: list[str] = []
    programme = decl.get("programme")
    if not isinstance(programme, dict):
        return ["programme: absent or not an object"]
    for key in PROGRAMME_SCALAR_KEYS:
        if not str(programme.get(key) or "").strip():
            findings.append(f"programme.{key}: absent")
    for key in PROGRAMME_REFERENCE_KEYS:
        value = str(programme.get(key) or "")
        if not value:
            findings.append(f"programme.{key}: absent")
        elif resolve_reference(value) is None:
            findings.append(f"programme.{key}: does not resolve: {value}")
    if not as_list(programme.get("forbidden_write_prefixes")):
        findings.append("programme.forbidden_write_prefixes: absent")

    for name, allowed in ALLOWED_KEYS.items():
        entries = section(decl, name)
        if not entries:
            findings.append(f"{name}: section is absent or empty")
            continue
        seen: set[str] = set()
        for entry in entries:
            ident = str(entry.get("id") or "")
            if not ident:
                findings.append(f"{name}: an entry carries no identifier")
                continue
            if ident in seen:
                findings.append(f"{name}: duplicate identifier {ident}")
            seen.add(ident)
            for key in entry:
                if key not in allowed:
                    findings.append(f"{name}.{ident}: carries an undeclared key {key!r}")

    substrate_ids = {str(entry.get("id")) for entry in section(decl, "substrate")}
    for name in ("discovery", "enrichment", "measures", "planes", "duplicates", "probes"):
        for entry in section(decl, name):
            ref = entry.get("substrate")
            if ref is not None and str(ref) not in substrate_ids:
                findings.append(f"{name}.{entry.get('id')}: names an undeclared substrate {ref!r}")

    dispositions = {str(entry.get("disposition")) for entry in section(decl, "dispositions")}
    rules = section(decl, "disposition_rules")
    for entry in rules:
        target = str(entry.get("disposition") or "")
        if target not in dispositions:
            findings.append(
                f"disposition_rules.{entry.get('id')}: names an undeclared disposition {target!r}"
            )
        for clause in as_list(entry.get("when")):
            if not isinstance(clause, dict):
                findings.append(f"disposition_rules.{entry.get('id')}: a clause is not an object")
                continue
            if str(clause.get("op") or "") not in PREDICATES:
                findings.append(
                    f"disposition_rules.{entry.get('id')}: unimplemented predicate "
                    f"{clause.get('op')!r}"
                )
    covered = {str(entry.get("disposition")) for entry in rules}
    for missing in sorted(dispositions - covered):
        findings.append(
            f"dispositions.{missing}: declared but no rule can ever assign it — a disposition "
            "with no rule is an unreachable outcome"
        )
    if rules and [item for item in as_list(rules[-1].get("when")) if isinstance(item, dict)]:
        findings.append(
            "disposition_rules: the final rule carries clauses, so the rule set is not total"
        )
    for index, entry in enumerate(rules[:-1]):
        if not [item for item in as_list(entry.get("when")) if isinstance(item, dict)]:
            findings.append(
                f"disposition_rules.{entry.get('id')}: a catch-all at position {index + 1} makes "
                "every later rule unreachable"
            )

    for entry in section(decl, "gaps"):
        if str(entry.get("op") or "") not in PREDICATES:
            findings.append(f"gaps.{entry.get('id')}: unimplemented predicate {entry.get('op')!r}")

    metrics_available = set(metric_names(decl))
    for name in ("verifications", "validations"):
        for entry in section(decl, name):
            if str(entry.get("metric") or "") not in metrics_available:
                findings.append(
                    f"{name}.{entry.get('id')}: names a metric the engine does not compute: "
                    f"{entry.get('metric')!r}"
                )
    for entry in section(decl, "gates"):
        if not as_list(entry.get("metrics")):
            findings.append(f"gates.{entry.get('id')}: binds no metric, so it can assert nothing")
        for metric in as_list(entry.get("metrics")):
            if str(metric) not in metrics_available:
                findings.append(f"gates.{entry.get('id')}: names an uncomputed metric {metric!r}")
    gate_ids = {str(entry.get("id")) for entry in section(decl, "gates")}
    severities = {str(entry.get("severity")) for entry in section(decl, "severities")}
    for entry in section(decl, "compliance"):
        if str(entry.get("gate") or "") not in gate_ids:
            findings.append(f"compliance.{entry.get('id')}: names an undeclared gate")
        if str(entry.get("severity_on_fail") or "") not in severities:
            findings.append(f"compliance.{entry.get('id')}: names an undeclared severity")
    matrix_ids = {str(entry.get("id")) for entry in section(decl, "matrices")}
    for entry in section(decl, "non_derivable"):
        for bound in as_list(entry.get("bounds")):
            if str(bound) not in matrix_ids:
                findings.append(f"non_derivable.{entry.get('id')}: bounds an undeclared matrix")
        probe = str(entry.get("probe") or "")
        if probe not in {str(item.get("id")) for item in section(decl, "probes")}:
            findings.append(f"non_derivable.{entry.get('id')}: names no declared counted probe")
        if resolve_reference(str(entry.get("owner") or "")) is None:
            findings.append(
                f"non_derivable.{entry.get('id')}: the owner of the unblocking act does not "
                f"resolve: {entry.get('owner')!r}"
            )
    if len(section(decl, "outputs")) < len(matrix_ids) // 2:
        findings.append("outputs: fewer outputs than the charter requires")
    for entry in section(decl, "references"):
        if resolve_reference(str(entry.get("path") or "")) is None:
            findings.append(f"references.{entry.get('id')}: does not resolve")
    for entry in section(decl, "matrices"):
        owner = entry.get("canonical_owner")
        if owner and resolve_reference(str(owner)) is None:
            findings.append(
                f"matrices.{entry.get('id')}: canonical owner does not resolve: {owner}"
            )
    return findings


def metric_names(decl: dict) -> list[str]:
    """The metric vocabulary, computed once from a real model over a fixed state."""
    sub = Substrate(decl)
    model = build_model(decl, sub, FIXED_STATE)
    return sorted(model["metrics"])


def _executable_source(source: str) -> str:
    """The source with comments and docstrings removed, so prose is not read as behaviour.

    THE RULE IS ABOUT SPECIAL-CASING, AND PROSE SPECIAL-CASES NOTHING. Measured against the
    whole file this check reported nine values as hard-coded, and every one of them sat in a
    comment or a docstring explaining WHY a gate behaves as it does — "GATE-04 is included
    transitively", "PLN-CODE and PLN-MODULE, the two planes that decide the acyclicity rule".
    None of them is reachable by the interpreter and none would need editing to extend the
    blueprint, which is the harm the rule names.

    Counting them had a second cost worth stating: it made the check unsatisfiable except by
    deleting the explanations, so the only way to go green was to destroy the reasoning the
    repository keeps deliberately. A detector that can only be satisfied by removing
    knowledge is measuring the wrong thing (adr/0042, and URKE-L-33 for the same shape in
    another programme).

    Comments and docstrings are stripped by tokenizing rather than by regex, so a `#` inside
    a string literal is not mistaken for a comment and a declared value quoted in real code
    is still caught.
    """
    import io
    import tokenize

    kept: list[str] = []
    previous = tokenize.INDENT
    try:
        for token in tokenize.generate_tokens(io.StringIO(source).readline):
            if token.type == tokenize.COMMENT:
                continue
            if token.type == tokenize.STRING and previous in (
                tokenize.INDENT,
                tokenize.DEDENT,
                tokenize.NEWLINE,
                tokenize.NL,
                tokenize.ENCODING,
            ):
                continue  # a docstring: the first statement of a module, class or function
            kept.append(token.string)
            if token.type not in (tokenize.NL, tokenize.COMMENT):
                previous = token.type
    except tokenize.TokenError:  # pragma: no cover - an untokenizable engine is a fault
        return source
    return "\n".join(kept)


def check_no_enumeration(decl: dict, sub: Substrate | None = None) -> list[str]:
    """Prove the blueprint is DATA: the engine may name none of its subject matter.

    A declared value counts as named only when it appears as a distinct token in the
    source, so an unrelated English word that merely contains a declared token as a
    substring is not a false positive — while any literal use of the token itself is.
    """
    findings: list[str] = []
    source = _executable_source(Path(__file__).read_text("utf-8"))
    literals: list[str] = []
    for name in ALLOWED_KEYS:
        literals += [str(entry.get("id")) for entry in section(decl, name) if entry.get("id")]
    literals += [str(entry.get("disposition")) for entry in section(decl, "dispositions")]
    literals += [str(entry.get("class")) for entry in section(decl, "discovery")]
    literals += [str(entry.get("severity")) for entry in section(decl, "severities")]
    literals += [str(entry.get("path")) for entry in section(decl, "substrate")]
    literals += [str(entry.get("selector")) for entry in section(decl, "discovery")]
    literals += [str(entry.get("name")) for entry in section(decl, "matrices")]
    literals += [
        str(entry.get("canonical_owner"))
        for entry in section(decl, "matrices")
        if entry.get("canonical_owner")
    ]
    literals += [str(entry.get("value")) for entry in section(decl, "tracking")]
    for literal in sorted({item for item in literals if item and item != "None"}):
        token = re.compile(r"(?<![A-Za-z0-9_])" + re.escape(literal) + r"(?![A-Za-z0-9_])")
        if token.search(source):
            findings.append(
                f"engine source special-cases declared value {literal!r} — extending the "
                "blueprint would require a code change"
            )
    return findings


def check_write_scope(
    decl: dict, sub: Substrate | None = None, written: list[Path] | None = None
) -> list[str]:
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
    """Every required substrate exists, is version-controlled, parses, and resolves."""
    substrate = sub if sub is not None else Substrate(decl)
    return substrate.findings()


def check_no_fabrication(decl: dict, sub: Substrate | None = None) -> list[str]:
    """Every emitted row must trace to a discovery source, a measure or a counted probe."""
    substrate = sub if sub is not None else Substrate(decl)
    model = build_model(decl, substrate, FIXED_STATE)
    findings: list[str] = []
    for unit in model["units"]:
        if not unit["sources"]:
            findings.append(f"{unit['unit_key']}: emitted with no originating discovery source")
        if not unit["disposition_rule"]:
            findings.append(f"{unit['unit_key']}: emitted with no rule behind its disposition")
    for record in model["matrices"]:
        if not record["resolves"]:
            findings.append(
                f"{record['id']}: neither bound to a resolving owner nor derivable here"
            )
        if record["restated"]:
            findings.append(f"{record['id']}: bound to an owner yet restates its rows here")
    for entry in model["non_derivable"]:
        probe = [item for item in model["probes"] if item["id"] == str(entry.get("probe"))]
        if not probe:
            findings.append(f"{entry.get('id')}: declared unknown with no executed probe")
        elif probe[0]["probed"] == 0:
            findings.append(
                f"{entry.get('id')}: probe measured nothing, so the absence is unproven"
            )
    for item in model["verifications"] + model["validations"]:
        if item["measured"] is None:
            findings.append(f"{item['id']}: obligation asserted over an uncomputed metric")
    return findings


def check_reuse_before_create(decl: dict, sub: Substrate | None = None) -> list[str]:
    """The zero-duplication invariant, mechanized."""
    findings: list[str] = []
    programme = decl.get("programme") or {}
    home = str(programme.get("operational_home") or "")
    for entry in section(decl, "matrices"):
        owner = str(entry.get("canonical_owner") or "")
        mode = str(entry.get("mode") or "")
        if not owner:
            continue
        if owner.startswith(home):
            findings.append(
                f"matrices.{entry.get('id')}: binds an owner inside this programme's own home — "
                "that is a create dressed as a reuse"
            )
        if resolve_reference(owner) is None and mode == "BOUND":
            findings.append(
                f"matrices.{entry.get('id')}: bound to an owner that does not resolve, so nothing "
                "is actually reused"
            )
    for entry in section(decl, "substrate"):
        path = str(entry.get("path") or "")
        if path.startswith(home):
            findings.append(
                f"substrate.{entry.get('id')}: reads this programme's own output as substrate — "
                "derived truth may not be its own input"
            )
    for key in PROGRAMME_REFERENCE_KEYS:
        value = str(programme.get(key) or "")
        if value and value != home and value.startswith(home):
            findings.append(f"programme.{key}: points inside this programme's own home")
    return findings


def check_totality(decl: dict, sub: Substrate | None = None) -> list[str]:
    """Every discovered unit carries exactly one disposition from the closed set."""
    substrate = sub if sub is not None else Substrate(decl)
    model = build_model(decl, substrate, FIXED_STATE)
    closed = {str(entry.get("disposition")) for entry in section(decl, "dispositions")}
    findings: list[str] = []
    for unit in model["units"]:
        if not unit["disposition"]:
            findings.append(f"{unit['unit_key']}: carries no disposition")
        elif unit["disposition"] not in closed:
            findings.append(
                f"{unit['unit_key']}: carries a disposition outside the closed set: "
                f"{unit['disposition']!r}"
            )
    rule_ids = {rule["id"] for rule in model["disposition_rules"]}
    for unit in model["units"]:
        if unit["disposition_rule"] and unit["disposition_rule"] not in rule_ids:
            findings.append(f"{unit['unit_key']}: names a rule that is not declared")
    return findings


FIXED_STATE = {
    # UCOS-RFP-001 RFP-2 — no commit identity is emitted, so none is neutralised here.
    "anchor": "the containing commit — owned by version control, never restated here",
    "detached": False,
    "working_tree": "CLEAN",
    "dirty_entries": 0,
    # Backlog item RB-05: the per-path list was removed — see observed_state(). This
    # determinism fixture must mirror the emitted shape exactly, or the determinism
    # self-guard would compare a key the engine no longer produces.
    "modified": 0,
    "deleted": 0,
    "untracked": 0,
    "conflicts": 0,
    "interrupted_operations": [],
    "broken_symlinks": [],
    "tracked_files": 0,
}


def self_determinism(decl: dict, sub: Substrate | None = None) -> list[str]:
    """Render the output set twice from one state; the bytes must be identical."""
    substrate = sub if sub is not None else Substrate(decl)
    first = render(decl, build_model(decl, substrate, FIXED_STATE))
    second = render(decl, build_model(decl, substrate, FIXED_STATE))
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
    "--check-totality": check_totality,
}


# ----------------------------------------------------------------------------- driver


#: UCOS-RC-003 — working-tree measurements are GATE INPUTS, never canonical identity.
#:
#: `dirty_entries_outside_generated` and its siblings count uncommitted entries in the tree
#: that is being measured. Persisting that count into a TRACKED file inside that same tree
#: is self-referential: this engine necessarily runs BEFORE the commit that carries its
#: output, so it always records the pre-commit dirt, while a pristine clone of that commit
#: computes something else. The Phase-9 forensic measured it directly — source `6`, clone
#: `23`, and after RC-001 removed `excluded_entries` this was the entire remaining
#: divergence in rib.json across nine fields.
#:
#: This is the defect RB-05 already identified and only half-closed. That item removed the
#: per-path LIST on exactly this reasoning ("Persisting a measurement of the working tree's
#: own dirtiness inside a TRACKED file is what the repository fixed-point principle
#: forbids -- running the gate became a mutation that changed the next measurement") and
#: kept the COUNT, which carries the identical defect at lower resolution.
#:
#: Nothing is weakened. The metric is still computed, still evaluated by GATE-12 and
#: VAL-02, still fail-closed, and still printed in the gate's stdout report where an
#: operator reads it. Only its serialization into the canonical artifact is withheld — the
#: verdict remains, so AEE still observes a CLOSED gate over a dirty tree, and the
#: repository still refuses to certify one.
_WORKING_TREE_MEASURES: frozenset[str] = frozenset(
    {
        "dirty_entries_outside_generated",
        "dirty_entries",
        "contamination_entries",
        "modified",
        "deleted",
        "untracked",
        "untracked_entries",
        "working_tree",
    }
)


def _working_tree_row(repo: dict) -> str:
    """The working-tree row of every rendered header.

    Rendered from the CANONICAL model, where both fields hold the observation's identity
    rather than a reading. Interpolating them into the old sentence produced
    "UCOS-OBS-000003 (UCOS-OBS-000003 entries…)" — byte-stable and correct, but it reads
    as a defect, and a register nobody trusts to be legible is a register nobody reads.
    So the row names the observation once and says plainly where the reading lives.
    """
    state = repo.get("working_tree")
    entries = repo.get("dirty_entries")
    if isinstance(state, str) and state.startswith("UCOS-OBS-"):
        return (
            f"observation `{state}` — reading withheld (Observation Truth, "
            "UCOS-OBSERVATION-UNIVERSE-001); the measurement is on this programme's "
            "evidence surface"
        )
    return (
        f"{state} ({entries} entries, measured outside this programme's own zone — RFP-3)"
    )


def seal_payload(model: dict) -> dict:
    """What a seal covers. THE single definition, applied to two planes.

    It is called once over the runtime model — the execution identity the stdout report
    and the evidence surface carry — and once over the canonical model inside
    :func:`canonical_model`, so the seal in rib.json summarises the CANONICAL verdicts.

    That it is one function rather than two literals is the whole point. Every verdict it
    reads is working-tree-dependent at runtime and commit-determined after redaction, so
    a second copy of this shape would drift the moment either plane gained a field — and
    a drifted seal is a fixed point that silently stops meaning anything.
    """
    return {
        "units": [
            {"id": unit["unique_id"], "key": unit["unit_key"], "disposition": unit["disposition"]}
            for unit in model.get("units", [])
        ],
        "gates": [{"id": g["id"], "verdict": g["verdict"]} for g in model.get("gates", [])],
        "verifications": [
            {"id": i["id"], "verdict": i["verdict"]} for i in model.get("verifications", [])
        ],
        "validations": [
            {"id": i["id"], "verdict": i["verdict"]} for i in model.get("validations", [])
        ],
        "gate": model.get("gate"),
        "determination": model.get("determination"),
    }


def _working_tree_observation_id() -> str | None:
    """This programme's working-tree observation, resolved to its Universal Identity.

    Read from the ONE identity authority (00-BOOK/DATA/id-ledger.json :: by_observation).
    This engine never mints — minting belongs to UCOS-UGA-001, and a second minter would
    be a second authority. Returns None when the observation has not been minted, so the
    caller keeps the original RC-003 placeholder rather than emitting a dangling id.
    """
    key = "UCOS-RIB-001::dirty-entries-outside-generated::WORKING_TREE_STATE"
    try:
        ledger = json.loads(
            (REPO / "00-BOOK" / "DATA" / "id-ledger.json").read_text(encoding="utf-8")
        )
    except (OSError, ValueError):
        return None
    record = (ledger.get("by_observation") or {}).get(key)
    return record.get("observation_id") if record else None


def _working_tree_scope(model: dict) -> tuple[set[str], set[str]]:
    """(validation ids, gate ids) whose verdict is a function of the WORKING TREE.

    Derived from the declared metrics, never from a hand-kept list, so a future gate that
    reads a working-tree measure is covered the day it is declared.

    GATE-04 is included transitively: it gates on `validations_failed`, which aggregates
    VAL-02 (working-tree cleanliness). Its canonical verdict is therefore recomputed from
    the validations that remain once the working-tree ones are set aside — so GATE-04
    still FAILS canonically for any other unmet validation. Nothing is excused.
    """
    wt_validations = {
        str(v.get("id"))
        for v in model.get("validations", [])
        if v.get("metric") in _WORKING_TREE_MEASURES
    }
    wt_gates = {
        str(g.get("id"))
        for g in model.get("gates", [])
        if set(g.get("metrics") or []) and set(g.get("metrics") or []) <= _WORKING_TREE_MEASURES
    }
    return wt_validations, wt_gates


def _observed_verdicts(model: dict) -> dict:
    """The runtime verdicts this pass actually observed — the reading, for evidence."""
    wt_validations, _wt_gates = _working_tree_scope(model)
    # Every gate that DECLARES a working-tree metric — the same rule the canonical
    # projection uses. Keying this to the all-or-nothing `wt_gates` set omitted GATE-12,
    # whose metrics are mixed, so the one verdict most affected by the tree was the one
    # the evidence did not record. Evidence must be complete or the relocation is a
    # deletion.
    return {
        "gate": model.get("gate"),
        "gate_exit": model.get("gate_exit"),
        "determination": model.get("determination"),
        "working_tree_gates": {
            str(g["id"]): g.get("verdict")
            for g in model.get("gates", [])
            if (set(g.get("metrics") or []) & _WORKING_TREE_MEASURES)
            or bool(g.get("working_tree_transitive"))
        },
        "working_tree_validations": {
            str(v["id"]): v.get("verdict")
            for v in model.get("validations", [])
            if str(v["id"]) in wt_validations
        },
        "compliance": model.get("compliance", []),
        "repository": model.get("repository", {}),
    }


def canonical_model(model: dict) -> dict:
    """The model with working-tree measurements withheld from serialization.

    Returns a copy; the in-memory model keeps every value so gate evaluation, the stdout
    report and the evidence index are unaffected.
    """

    # UCOS-OBSERVATION-UNIVERSE-001 — a redaction hides the reading but points at nothing,
    # so the evidence it withholds is untraceable. The placeholder is replaced by the
    # observation's stable Universal Identity: byte-stable exactly as the placeholder was,
    # and now resolvable to the surface that holds the reading. Falls back to the original
    # placeholder only if the identity authority has not yet minted the observation, so
    # this engine never blocks on UCOS-UGA-001 and never emits a dangling reference.
    withheld = _working_tree_observation_id() or (
        "<withheld: working-tree measurement, UCOS-RC-003>"
    )

    def redact_text(text: str) -> str:
        """Redact `metric=value` renderings, which is how gates and compliance carry it."""
        for metric in _WORKING_TREE_MEASURES:
            text = re.sub(rf"\b{re.escape(metric)}=\S+", f"{metric}={withheld}", text)
        return text

    def strip(node: object) -> object:
        if isinstance(node, dict):
            # A validation carries its subject in `metric` and its reading in `measured`,
            # so the reading is only identifiable through its sibling.
            measured_is_working_tree = node.get("metric") in _WORKING_TREE_MEASURES
            out: dict[str, object] = {}
            for k, v in node.items():
                if k in _WORKING_TREE_MEASURES and isinstance(v, int | str):
                    out[k] = withheld
                elif k == "measured" and measured_is_working_tree:
                    out[k] = withheld
                elif isinstance(v, str):
                    out[k] = redact_text(v)
                else:
                    out[k] = strip(v)
            return out
        if isinstance(node, list):
            return [redact_text(v) if isinstance(v, str) else strip(v) for v in node]
        if isinstance(node, str):
            return redact_text(node)
        return node

    stripped = strip(model)
    assert isinstance(stripped, dict)

    # UCOS-OBSERVATION-UNIVERSE-001 (OBS-INV-07/10) — redaction was not enough.
    #
    # Blanking a VALUE cannot blank a list ELEMENT. `compliance` gained a CMP-CLEAN entry
    # when the tree was dirty and lost it when clean, and `gate`/`determination`/
    # `gate_exit` flipped with it — so rib.json still moved with the working tree even
    # though every measurement in it was withheld. This engine runs as an actuator INSIDE
    # a UCOS-AEE-001 pass, where earlier actuators necessarily dirty the tree, so no
    # ordering could ever let it observe a clean one: it rewrote sixteen files every
    # round and Phase 8 held at zero_drift_rounds=0.
    #
    # The canonical projection now carries the COMMIT-DETERMINED verdict — what the
    # blueprint says about the repository at this commit — and the working-tree verdict
    # becomes an observation reference. GATE-04 is RECOMPUTED rather than excused: it
    # still fails canonically for any non-working-tree validation that is unmet.
    #
    # NOTHING IS WEAKENED. The runtime model keeps every verdict, `gate_exit` below is
    # unchanged so the process still exits non-zero over a dirty tree, the stdout report
    # still names the failure, and the full reading is written to
    # evidence/observations/RIB/ where it stays auditable.
    wt_validations, wt_gates = _working_tree_scope(model)
    observation = _working_tree_observation_id() or withheld

    canonical_validation_failures = sum(
        1
        for v in model.get("validations", [])
        if str(v.get("id")) not in wt_validations and v.get("verdict") != "PASS"
    )
    for entry in stripped.get("validations", []):
        if str(entry.get("id")) in wt_validations:
            entry["verdict"] = observation

    # Uniform, per-FAILURE rather than per-gate. GATE-12 declares three metrics — dirty
    # entries, unclassified ignored paths, shadowed tracked paths — and only the first is
    # a working-tree reading. Excusing the whole gate would have excused the other two,
    # which is the weakening this remediation forbids. So each failure is judged on its
    # own metric and the verdict is recomputed from those that remain: GATE-12 still
    # FAILS canonically the moment an ignored path is unclassified.
    observed_gate_ids: set[str] = set()
    for gate in stripped.get("gates", []):
        gid = str(gate.get("id"))
        original = list(gate.get("failures") or [])
        remaining = [
            f for f in original
            if not any(str(f).startswith(m) for m in _WORKING_TREE_MEASURES)
        ]
        if gate.get("working_tree_transitive"):
            remaining = [f for f in remaining if canonical_validation_failures]
        # Attached on DECLARATION, never on outcome. Keying it to "was a failure filtered"
        # would put the reading back into the artifact as key PRESENCE — the same
        # membership leak that made redaction insufficient in the first place.
        declares_working_tree = bool(
            set(gate.get("metrics") or []) & _WORKING_TREE_MEASURES
        ) or bool(gate.get("working_tree_transitive"))
        if declares_working_tree:
            observed_gate_ids.add(gid)
            gate["working_tree_verdict_observation"] = observation
        gate["failures"] = remaining
        gate["verdict"] = "PASS" if not remaining else "FAIL"

    stripped["compliance"] = [
        finding
        for finding in stripped.get("compliance", [])
        if next((g for g in stripped.get("gates", [])
                 if str(g.get("id")) == str(finding.get("gate"))), {}).get("verdict") == "FAIL"
    ]

    canonical_open = all(
        g.get("verdict") == "PASS"
        for g in stripped.get("gates", [])
        if g.get("blocking")
    )
    stripped["gate"] = "OPEN" if canonical_open else "CLOSED"
    stripped["gate_exit"] = 0 if canonical_open else 1
    stripped["determination"] = (
        model["determination"] if canonical_open == (model.get("gate") == "OPEN")
        else ("BLUEPRINT CERTIFIED — REPOSITORY MAY PROCEED" if canonical_open
              else "BLUEPRINT NOT CERTIFIED — REPOSITORY MUST STOP")
    )
    stripped["working_tree_verdict_observation"] = observation

    # UCOS-OBSERVATION-UNIVERSE-001 `derived_observation_rule` — THE UNIVERSAL RULE.
    #
    # Everything above recomputes the canonical VERDICTS from the redacted structures. The
    # AGGREGATES OVER those verdicts were not recomputed, and they are computed far
    # upstream — `metrics["gates_passed"]` and `metrics["blocking_failed"]` at the model
    # build (see the `metrics.update` block), from the RUNTIME gates, before this function
    # is ever called. So the artifact carried `gate: OPEN`, `gates[]` all PASS and
    # `gates_passed: 10` simultaneously, and moved with the working tree through numbers
    # that are not spelled like a leak. Phase 8 held at zero_drift_rounds=0.
    #
    # The remedy is the rule, not a patch: A CANONICAL AGGREGATE IS DERIVED FROM CANONICAL
    # STRUCTURES. Each metric below is re-derived from `stripped`, so a future gate,
    # validation or finding is covered the day it is declared — there is no list of leaking
    # metric names here to fall out of date, because the aggregates are recomputed from the
    # structures they summarise rather than filtered by name.
    #
    # NOTHING IS WEAKENED. The runtime model keeps every count, `gate_exit` is unchanged,
    # the stdout report still names the failure, and the full reading is written to
    # evidence/observations/RIB/ under the observation's Universal Identity.
    canonical_metrics = dict(stripped.get("metrics") or {})
    canonical_gates = stripped.get("gates", [])
    canonical_metrics["gates_passed"] = len(
        [g for g in canonical_gates if not g.get("failures")]
    )
    canonical_metrics["blocking_failed"] = [
        g["id"] for g in canonical_gates if g.get("blocking") and g.get("failures")
    ]
    canonical_metrics["validations_failed"] = canonical_validation_failures
    canonical_metrics["compliance_findings"] = len(stripped.get("compliance", []))
    stripped["metrics"] = canonical_metrics

    # The same rule one level out: `contamination.clean` is a one-bit copy of
    # `contamination_entries`, which `strip` already withheld. A boolean is a lower
    # resolution of a count, and the resolution of a copy is not what makes it a copy.
    repository = stripped.get("repository")
    if isinstance(repository, dict):
        contamination = repository.get("contamination")
        if isinstance(contamination, dict) and "clean" in contamination:
            contamination = dict(contamination)
            contamination["clean"] = observation
            repository = dict(repository)
            repository["contamination"] = contamination
            stripped["repository"] = repository

    # The seal is the outermost derived value, and it was the last one still leaking.
    # `build_model` computes it over the RUNTIME gates, validations, gate and
    # determination — every one of which is working-tree-dependent — and the strip
    # carried the result through untouched. Measured: identical substrate hashes, seal
    # 13b54470 over a dirty tree and 69fffed4 over a clean one, which is registry_variance
    # and ordering_variance in Phase 8 for as long as the chain dirties the tree it runs
    # in. Re-derived here from the canonical structures, through the SAME payload
    # function, so a seal summarises the verdicts the artifact actually states.
    stripped["seal_sha256"] = digest(seal_payload(stripped))
    return stripped


def _emit_observation_evidence(model: dict) -> Path:
    """The runtime reading canonical_model() lifted out. Relocated, never deleted."""
    target = HERE / "evidence" / "observations" / "RIB"
    target.mkdir(parents=True, exist_ok=True)
    path = target / f"{_working_tree_observation_id() or 'OBS-RIB-UNMINTED'}.json"
    path.write_text(
        json.dumps(
            {
                "authority": "NONE — EVIDENCE. Observation Truth, never canonical identity.",
                "evidence_class": "EXECUTION",
                "binds": "UCOS-OBSERVATION-UNIVERSE-001",
                "observation_id": _working_tree_observation_id(),
                "observer": "UCOS-RIB-001",
                "reading": _observed_verdicts(model),
            },
            indent=2,
            sort_keys=True,
            ensure_ascii=False,
        )
        + "\n",
        encoding="utf-8",
    )
    return path


def write_outputs(decl: dict, model: dict) -> list[Path]:
    """Every canonical surface is rendered from the CANONICAL model.

    UCOS-OBSERVATION-UNIVERSE-001 `derived_observation_rule`. Only rib.json used to be
    projected; the fifteen Markdown registers were rendered straight from the runtime
    model, so their headers carried `WORKING TREE | DIRTY (5 entries)`, `GATES | 10/12`,
    the runtime determination and the runtime seal — every one of them an observation, in
    files the generated-artifact registry declares CANONICAL and one of which
    (10-IMPLEMENTATION-QUEUE.md) is the Phase-8 `ordering_variance` dimension.
    A rendered sentence is a lower-resolution copy of the value it renders.

    The projection is computed ONCE and shared, which also closes the gap that let
    rib.json and its own dashboard state two different seals for one run.

    The runtime model is still passed to :func:`_emit_observation_evidence`, because the
    evidence surface is exactly where the reading belongs.
    """
    canonical = canonical_model(model)
    written: list[Path] = []
    for filename, text in sorted(render(decl, canonical).items()):
        target = HERE / filename
        target.write_text(text, encoding="utf-8")
        written.append(target)
    model_path = HERE / MODEL_FILE
    model_path.write_text(canonical_json(canonical), encoding="utf-8")
    written.append(model_path)
    _emit_observation_evidence(model)
    EVIDENCE_DIR.mkdir(exist_ok=True)
    index_path = EVIDENCE_DIR / EVIDENCE_INDEX
    index_path.write_text(
        canonical_json(
            {
                "substrate": model["substrate"],
                "discovery": model["discovery"],
                "measures": model["measures"],
                "planes": [
                    {
                        "id": plane["id"],
                        "kind": plane["kind"],
                        "nodes": plane["nodes"],
                        "edges": plane["edges"],
                        "cycles": plane["cycles"],
                    }
                    for plane in model["planes"]
                ],
                "probes": model["probes"],
                "metrics": model["metrics"],
                "verifications": model["verifications"],
                "validations": model["validations"],
                "gates": model["gates"],
                "seal_sha256": model["seal_sha256"],
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
    programme_id = str((decl.get("programme") or {}).get("id") or "")

    for flag, check in SELF_CHECKS.items():
        if getattr(args, flag.lstrip("-").replace("-", "_")):
            substrate = Substrate(decl)
            findings = check(decl, substrate)
            label = flag.lstrip("-")
            if findings:
                print(f"{programme_id} {label}: FAIL")
                for finding in findings:
                    print(f"  - {finding}")
                return 1
            print(f"{programme_id} {label}: PASS")
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
        f"{programme_id}: {model['determination']} | "
        f"units={m['unit_total']} | "
        f"sources={len(model['discovery'])} | "
        f"substrate={m['substrate_usable']}/{m['substrate_total']} | "
        f"matrices={m['matrices_bound']}bound/{m['matrix_total']} | "
        f"queued={m['queued_total']}in{m['wave_total']}waves | "
        f"gates={m['gates_passed']}/{m['gate_total']} | "
        f"dirty={m['dirty_entries_outside_generated']} | "
        f"gate={model['gate']} | seal={model['seal_sha256'][:16]}"
    )
    if not args.gate:
        print(f"wrote {len(written)} artifacts to {HERE}")
        return 0
    for gate in model["gates"]:
        if gate["blocking"] and gate["failures"]:
            print(
                f"  - {gate['id']} {gate['name']}: {'; '.join(gate['failures'])}",
                file=sys.stderr,
            )
    return model["gate_exit"]


if __name__ == "__main__":
    raise SystemExit(main())
