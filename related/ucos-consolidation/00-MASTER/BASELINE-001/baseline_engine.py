"""BASELINE-001 — Universal Constitutional Baseline Inheritance.

AUTHORITY = NONE (DERIVED TRUTH). This engine creates no baseline, advances no baseline,
certifies nothing, ratifies nothing, freezes nothing and occupies no tier. Every baseline it
registers is DISCOVERED by reading the located register that already records it; every
inheritance and non-inheritance rule it binds is a clause it reads out of a located instrument;
every disagreement it finds between the register that records currency and another register
that claims it is reported and referred to the claim owner, never decided here.

The records this measurement reads are append-only. It never writes one: the write set is
proved disjoint from the located record set by --check-record-immutability, which also proves
that every record present in the programme home is a member of the protected set, so a record
cannot be quietly dropped from protection to make room for a generated page.

    python3 00-MASTER/BASELINE-001/baseline_engine.py --render     # regenerate the registers
    python3 00-MASTER/BASELINE-001/baseline_engine.py --gate       # fail-closed baseline gate
    python3 00-MASTER/BASELINE-001/baseline_engine.py --check-declaration
    python3 00-MASTER/BASELINE-001/baseline_engine.py --check-no-enumeration
    python3 00-MASTER/BASELINE-001/baseline_engine.py --check-write-scope
    python3 00-MASTER/BASELINE-001/baseline_engine.py --check-determinism
    python3 00-MASTER/BASELINE-001/baseline_engine.py --check-knowledge-once
    python3 00-MASTER/BASELINE-001/baseline_engine.py --check-record-immutability
    python3 00-MASTER/BASELINE-001/baseline_engine.py --check-no-elevation

Exit semantics:
    0  every blocking validation satisfied — gate OPEN
    1  a blocking validation unsatisfied, or a self-guard failed — gate CLOSED
    2  fail-closed abort — the declaration is unusable, so no verdict may be asserted

Every register pointer, scheme pointer, succession reader, release pointer, version source,
lineage source, inheritance rule, non-inheritance rule, scope rule, ceiling, currency claim,
citation surface, record, continuation pointer and validation dimension is read from
baseline-declaration.json. No baseline identifier, no commit identity, no ordinal and no
release identifier appears as a literal below, which is what makes extension an edit to DATA
and to the located records rather than to code.

Stdlib only. No network. No version-control observation. No timestamp, no duration, no commit
identity and no absolute path is emitted, so the sealed output set is byte-identical for an
unchanged repository.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
DECLARATION = HERE / "baseline-declaration.json"
MODEL = HERE / "baseline.json"
OWN_PREFIX = HERE.relative_to(REPO).as_posix() + "/"

REQUIRED_SECTIONS = (
    "programme",
    "capabilities",
    "baseline_register",
    "scheme_source",
    "succession_source",
    "release_source",
    "version_sources",
    "lineage_source",
    "inheritance_rules",
    "non_inheritance_rules",
    "scope_rules",
    "ceiling",
    "certification_source",
    "currency_claims",
    "citation_surfaces",
    "record_set",
    "continuation_source",
    "elevation_prohibitions",
    "validations",
    "exit_criteria",
)

# The pages this measurement writes. Declared here so the write-scope, determinism and
# record-immutability guards all measure the SAME set the renderer produces.
PAGES = (
    "00-BASELINE-INHERITANCE-DASHBOARD.md",
    "01-SUCCESSION-AND-ADDRESSABILITY-REGISTER.md",
    "02-INHERITANCE-AND-NON-INHERITANCE-REGISTER.md",
    "03-CURRENCY-AND-CITATION-REGISTER.md",
    "04-VERSION-LINEAGE-AND-EVOLUTION-REGISTER.md",
    "05-VALIDATION-REPORT.md",
    "06-CERTIFICATION-REPORT.md",
)

# Reader kinds a currency claim may declare. A kind outside this set is a fail-closed
# violation: it is how an unimplemented reader would otherwise pass silently.
CLAIM_KINDS = ("markdown-field", "markdown-citations", "json-pointer")

# Currency outcomes. Properties DERIVED from two readings, never properties of a claim's
# identity. A divergence is referred to the claim owner and is never adjudicated here.
OUT_AGREES = "AGREES"
OUT_DIVERGES = "DIVERGES-REFERRED"
OUT_UNREADABLE = "UNREADABLE"

# Extensions a repository pointer may carry. A token without one of these is prose, not a
# pointer, and is deliberately not held to resolution.
POINTER_EXTENSIONS = ("md", "json", "txt", "py", "sh")


class FailClosed(Exception):
    """Raised when no verdict may be asserted. Always exits 2."""


# ---------------------------------------------------------------------------
# declaration


def load_declaration() -> dict:
    if not DECLARATION.exists():
        raise FailClosed(f"declaration not found: {DECLARATION.name}")
    try:
        document = json.loads(DECLARATION.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise FailClosed(f"declaration is not valid JSON: {exc}") from exc
    if not isinstance(document, dict):
        raise FailClosed("declaration is not an object")
    missing = [key for key in REQUIRED_SECTIONS if key not in document]
    if missing:
        raise FailClosed(f"declaration is missing required section(s): {', '.join(missing)}")
    if not document["record_set"].get("records"):
        raise FailClosed("declaration protects no record, so immutability cannot be measured")
    if not document["capabilities"]:
        raise FailClosed("declaration names no capability, so there is nothing to discharge")
    return document


def read_text(relative: str) -> str | None:
    """Read a located file, or None when it does not resolve. Never raises."""
    target = REPO / relative
    if not target.is_file():
        return None
    try:
        return target.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return None


def digest(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def repository_roots() -> set[str]:
    """The top-level names of the repository: how a pointer is told from prose shorthand."""
    try:
        return {entry.name for entry in REPO.iterdir()}
    except OSError:  # pragma: no cover - the repository root always reads
        return set()


def rendered_names() -> list[str]:
    """Everything this measurement writes, model included."""
    return sorted(PAGES) + [MODEL.name]


# ---------------------------------------------------------------------------
# readers — each returns what a LOCATED record says, and never raises


def split_row(line: str) -> list[str]:
    """Split one markdown row into stripped cells, with emphasis and code marks removed."""
    cells = line.strip().strip("|").split("|")
    return [cell.strip().replace("**", "").strip().strip("`").strip() for cell in cells]


def table_rows(text: str, section: str | None) -> list[list[str]]:
    """The data rows of the first pipe table at or after `section`.

    A separator row (all dashes) is dropped, and so is the header row that precedes it, so a
    column position is read from the declaration rather than guessed from the header text.
    """
    lines = text.splitlines()
    start = 0
    if section:
        for index, line in enumerate(lines):
            if line.strip() == section.strip():
                start = index + 1
                break
        else:
            return []
    rows: list[list[str]] = []
    in_table = False
    for line in lines[start:]:
        stripped = line.strip()
        if stripped.startswith("|"):
            in_table = True
            cells = split_row(stripped)
            if cells and all(set(cell) <= set("-: ") for cell in cells if cell):
                rows = []  # separator reached: everything before it was the header
                continue
            rows.append(cells)
            continue
        if in_table and not stripped:
            break
    return rows


def heading_block(text: str, heading: str) -> str | None:
    """The block from a heading line to the next heading of the same or shallower depth."""
    lines = text.splitlines()
    target = heading.strip()
    depth = len(target) - len(target.lstrip("#"))
    start = next((index for index, line in enumerate(lines) if line.strip() == target), None)
    if start is None:
        return None
    end = len(lines)
    for index in range(start + 1, len(lines)):
        stripped = lines[index].lstrip()
        if not stripped.startswith("#"):
            continue
        if len(stripped) - len(stripped.lstrip("#")) <= depth:
            end = index
            break
    return "\n".join(lines[start:end])


def named_block(text: str, needle: str, prefix: str) -> str | None:
    """The block of a document from the heading naming `needle` to the next heading."""
    lines = text.splitlines()
    start = next(
        (index for index, line in enumerate(lines) if line.startswith(prefix) and needle in line),
        None,
    )
    if start is None:
        return None
    end = next(
        (index for index in range(start + 1, len(lines)) if lines[index].startswith(prefix)),
        len(lines),
    )
    return "\n".join(lines[start:end])


def read_register(source: dict) -> tuple[list[dict], str | None]:
    """Discover the recorded baselines from the located register's table."""
    owner = source.get("owner")
    text = read_text(owner) if owner else None
    if text is None:
        return [], f"owner does not resolve: {owner}"
    pattern = source.get("id_pattern")
    if not pattern:
        return [], "no id_pattern declared"
    matcher = re.compile(rf"^({pattern})$")
    index = int(source["id_column"])
    ordinal_index = int(source["ordinal_column"])
    columns = source.get("columns") or {}
    records: list[dict] = []
    for cells in table_rows(text, source.get("section")):
        if len(cells) <= index:
            continue
        found = matcher.match(cells[index])
        if not found:
            continue
        record = {
            "id": found.group(1),
            "row": cells[ordinal_index] if ordinal_index < len(cells) else "",
        }
        for field, position in sorted(columns.items()):
            record[field] = cells[position] if position < len(cells) else ""
        records.append(record)
    if not records:
        return [], f"no baseline row matched under the declared section in {owner}"
    return records, None


def read_json_collection(owner: str, pointer: str) -> tuple[list[dict], str | None]:
    text = read_text(owner)
    if text is None:
        return [], f"owner does not resolve: {owner}"
    try:
        document = json.loads(text)
    except json.JSONDecodeError as exc:
        return [], f"owner is not valid JSON: {exc}"
    collection = document.get(pointer)
    if not isinstance(collection, list):
        return [], f"pointer does not resolve to a collection: {pointer}"
    return [entry for entry in collection if isinstance(entry, dict)], None


def read_json_mapping(owner: str, pointer: str) -> tuple[dict[str, dict], str | None]:
    """Read a PATH-KEYED MAPPING source, the shape the object ledger uses.

    read_json_collection requires a list, and the identity of an executable object is not
    held in one. 00-BOOK/DATA/id-ledger.json keys by_object BY PATH, so a source declared
    against it needs this shape rather than a collection pointer.
    """
    text = read_text(owner)
    if text is None:
        return {}, f"owner does not resolve: {owner}"
    try:
        document = json.loads(text)
    except json.JSONDecodeError as exc:
        return {}, f"owner is not valid JSON: {exc}"
    mapping = document.get(pointer)
    if not isinstance(mapping, dict):
        return {}, f"pointer does not resolve to a mapping: {pointer}"
    return {k: v for k, v in mapping.items() if isinstance(v, dict)}, None


def read_json_pointer(owner: str, pointer: str) -> tuple[str | None, str | None]:
    """Read a dotted path out of a located JSON declaration. Never raises."""
    text = read_text(owner)
    if text is None:
        return None, f"owner does not resolve: {owner}"
    try:
        node = json.loads(text)
    except json.JSONDecodeError as exc:
        return None, f"owner is not valid JSON: {exc}"
    for part in pointer.split("."):
        if not isinstance(node, dict) or part not in node:
            return None, f"pointer does not resolve: {pointer}"
        node = node[part]
    return (str(node) if node is not None else None), None


def read_field(text: str, label: str) -> str | None:
    """The value cell of a Field/Value row whose first column is `label`."""
    matcher = re.compile(rf"^\|\s*{re.escape(label)}\s*\|(?P<value>[^|]*)\|", re.MULTILINE)
    found = matcher.search(text)
    return found.group("value") if found else None


def read_items(text: str, anchor: str, prefix: str) -> list[str]:
    """Discover a bulleted list beginning after the anchor line, stopping at its end."""
    lines = text.splitlines()
    start = next((index + 1 for index, line in enumerate(lines) if anchor in line), None)
    if start is None:
        return []
    items: list[str] = []
    for line in lines[start:]:
        stripped = line.strip()
        if stripped.startswith(prefix):
            items.append(stripped[len(prefix) :].strip())
            continue
        if items and (not stripped or stripped.startswith(("#", "---"))):
            break
    return items


def pointers(text: str, roots: set[str]) -> list[str]:
    """Repository pointers in a text: a path whose first segment is a repository root.

    A bare filename, or a path whose first segment is not a repository root, is prose
    shorthand for a pointer given in full elsewhere and is deliberately not held to
    resolution. Holding prose to resolution would report writing style as evidence rot.
    """
    found: set[str] = set()
    extensions = "|".join(POINTER_EXTENSIONS)
    for token in re.findall(rf"[0-9A-Za-z_./\u03a9\u221e-]+\.(?:{extensions})", text):
        if "/" not in token:
            continue
        if token.split("/", 1)[0] not in roots:
            continue
        found.add(token)
    return sorted(found)


def strip_reference(value: str, separators: list[str]) -> str:
    """Drop a clause or parenthetical suffix from a declared reference."""
    candidate = value.strip().strip("`").strip()
    for separator in separators:
        candidate = candidate.split(separator)[0]
    return candidate.strip().strip("`").strip()


def surface_files(surfaces: list[str], extensions: list[str]) -> list[str]:
    """Every located file under the declared surfaces, deterministically ordered."""
    found: set[str] = set()
    for surface in surfaces:
        target = REPO / surface
        if target.is_file():
            found.add(surface)
            continue
        if not target.is_dir():
            continue
        for path in target.rglob("*"):
            if path.is_file() and path.suffix in extensions:
                found.add(path.relative_to(REPO).as_posix())
    return sorted(found)


def normalize(text: str) -> str:
    """Compare prose by meaning-preserving shape: no case, no marks, no parentheticals."""
    stripped = re.sub(r"\([^)]*\)", " ", text)
    stripped = stripped.replace("`", "").replace("*", "")
    return re.sub(r"[^a-z0-9=]+", " ", stripped.lower()).strip()


def bind_rules(rules: list[dict]) -> tuple[list[dict], list[str]]:
    """Bind each declared rule to its located clause, verifying the clause text is present."""
    bound: list[dict] = []
    problems: list[str] = []
    for rule in rules:
        text = read_text(rule["owner"])
        present = text is not None and rule["anchor"] in text
        bound.append(
            {"id": rule["id"], "rule": rule["rule"], "owner": rule["owner"], "bound": present}
        )
        if not present:
            problems.append(f"{rule['id']}: anchor absent in {rule['owner']}")
    return bound, problems



# ---------------------------------------------------------------------------
# measurement

# Which declared dimensions a capability's discharge depends on. A capability is discharged
# only when its measure ran, its population is non-empty, and every dimension it stands for is
# free of measured failures. Keyed by MEASURE, so no capability identifier appears here.
CAPABILITY_GATES: dict[str, tuple[str, ...]] = {
    "baselines_registered": ("BLN-VAL-01",),
    "records_resolved": ("BLN-VAL-04",),
    "identifiers_conformant": ("BLN-VAL-02",),
    "ordinals_addressable": ("BLN-VAL-03",),
    "lineage_measured": ("BLN-VAL-18",),
    "successions_linked": ("BLN-VAL-05", "BLN-VAL-06", "BLN-VAL-07"),
    "inheritance_rules_bound": ("BLN-VAL-13", "BLN-VAL-14"),
    "versions_succeeded": ("BLN-VAL-17",),
    "releases_corroborated": ("BLN-VAL-19",),
    "currency_claims_measured": ("BLN-VAL-12",),
    "ceiling_disclosed": ("BLN-VAL-16",),
    "certification_states_read": ("BLN-VAL-23",),
    "authority_disclosures": ("BLN-VAL-24",),
    "pointers_resolved": ("BLN-VAL-11",),
    "dependency_models_resolved": ("BLN-VAL-11",),
    "configuration_versions_read": ("BLN-VAL-17",),
    "scope_rules_bound": ("BLN-VAL-22",),
    "criteria_corroborated": ("BLN-VAL-21",),
    "continuation_bound": ("BLN-VAL-25",),
    "elevation_prohibitions_bound": ("BLN-VAL-15",),
}


def measure_baselines(document: dict, roots: set[str]) -> dict:  # noqa: C901 - one pass per row
    """Discover the recorded baselines and everything each row is required to carry."""
    register = document["baseline_register"]
    succession = document["succession_source"]
    scheme = document["scheme_source"]
    ceiling = document["ceiling"]
    rows, register_reason = read_register(register)
    register_text = read_text(register["owner"]) or ""
    current_token = str(register["current_token"]).upper()
    terminal = str(ceiling["terminal_token"]).upper()
    separators = list(succession["record_suffix_separators"])
    predecessor_matcher = re.compile(succession["predecessor_pattern"], re.MULTILINE)
    identifier_matcher = re.compile(register["id_pattern"])
    ordinal_matcher = re.compile(scheme["ordinal_pattern"])

    vocabulary_text = read_text(document["certification_source"]["owner"]) or ""
    vocabulary = set(
        re.findall(document["certification_source"]["vocabulary_pattern"], vocabulary_text)
    )

    recorded = [row["id"] for row in rows]
    baselines: list[dict] = []
    resolution: list[str] = []
    explicit: list[str] = []
    consistency: list[str] = []
    pointer: list[str] = []
    states: list[str] = []
    elevation: list[str] = []

    for index, row in enumerate(rows):
        target = strip_reference(str(row.get("record", "")), separators)
        block_owner: str | None = None
        block: str | None = None
        if target and (REPO / target).is_file():
            block_owner, block = target, read_text(target)
        else:
            block = named_block(register_text, row["id"], succession["section_prefix"])
            block_owner = register["owner"] if block is not None else None
        if block is None:
            resolution.append(f"{row['id']}: no evidence block resolves")

        claimed: list[str] = []
        if block:
            for found in predecessor_matcher.finditer(block):
                claimed.extend(identifier_matcher.findall(found.group("value")))
        claimed = sorted(set(claimed))
        structural = rows[index - 1]["id"] if index else None
        origin = structural is None
        if origin and claimed:
            explicit.append(f"{row['id']}: the origin records a predecessor")
        if not origin and not claimed:
            explicit.append(
                f"{row['id']}: records no explicit predecessor "
                "(implicit inheritance is prohibited)"
            )
        for candidate in claimed:
            if candidate not in recorded:
                consistency.append(f"{row['id']}: claims a predecessor that is not recorded")
            elif candidate != structural:
                consistency.append(
                    f"{row['id']}: the explicit predecessor is not the preceding baseline"
                )

        block_pointers = pointers(block or "", roots)
        unresolved = [item for item in block_pointers if not (REPO / item).exists()]
        pointer.extend(f"{row['id']}: {item}" for item in unresolved)

        state = str(row.get("state", ""))
        upper = state.upper()
        if not any(token in upper for token in vocabulary):
            states.append(f"{row['id']}: records no located lifecycle-status token")
        if terminal and terminal in upper:
            elevation.append(f"{row['id']}: records the terminal finality token")

        found_ordinal = ordinal_matcher.match(row["id"])
        baselines.append(
            {
                "id": row["id"],
                "row": row["row"],
                "ordinal": int(found_ordinal.group("ordinal")) if found_ordinal else None,
                "conformant": found_ordinal is not None,
                "commit_recorded": bool(str(row.get("commit", "")).strip()),
                "branch_recorded": bool(str(row.get("branch", "")).strip()),
                "date_recorded": bool(str(row.get("date", "")).strip()),
                "state": state,
                "record": str(row.get("record", "")),
                "block": block_owner,
                "pointers": len(block_pointers),
                "pointers_unresolved": unresolved,
                "predecessor_claimed": claimed,
                "predecessor_structural": structural,
                "origin": origin,
                "current": current_token in upper,
            }
        )

    return {
        "register_text": register_text,
        "register_reason": register_reason,
        "recorded": recorded,
        "baselines": baselines,
        "resolution": resolution,
        "explicit": explicit,
        "consistency": consistency,
        "pointer": pointer,
        "states": states,
        "elevation": elevation,
        "identifier_matcher": identifier_matcher,
    }


def measure_chain(baselines: list[dict]) -> tuple[dict, list[str]]:
    """The shape of the succession chain: one origin, one head, acyclic, fully covered."""
    problems: list[str] = []
    predecessors = {
        entry["id"]: (entry["predecessor_claimed"][0] if entry["predecessor_claimed"] else None)
        for entry in baselines
    }
    origins = [entry["id"] for entry in baselines if entry["origin"]]
    claimed = {value for value in predecessors.values() if value}
    heads = [entry["id"] for entry in baselines if entry["id"] not in claimed]
    if len(origins) != 1:
        problems.append("the chain does not have exactly one origin")
    if len(heads) != 1:
        problems.append("the chain does not have exactly one head")
    for start in sorted(predecessors):
        trail: list[str] = []
        node: str | None = start
        while node:
            if node in trail:
                problems.append(f"{start}: the succession chain is cyclic")
                break
            trail.append(node)
            node = predecessors.get(node)
    reachable: set[str] = set()
    if len(heads) == 1:
        node = heads[0]
        while node and node not in reachable:
            reachable.add(node)
            node = predecessors.get(node)
        problems.extend(
            f"{item}: not reachable from the head" for item in sorted(set(predecessors) - reachable)
        )
    chain = {
        "origins": origins,
        "heads": heads,
        "predecessors": predecessors,
        "acyclic": not any("cyclic" in item for item in problems),
    }
    return chain, problems


def measure_currency(
    document: dict, recorded: list[str], current: list[str], matcher: re.Pattern[str]
) -> tuple[list[dict], list[str], list[str]]:
    """Read every located claim of currency on both sides. Divergence is referred, never decided."""
    claims: list[dict] = []
    unreadable: list[str] = []
    divergences: list[str] = []
    for claim in document["currency_claims"]:
        kind = claim.get("kind")
        if kind not in CLAIM_KINDS:
            raise FailClosed(f"currency claim {claim.get('id')} declares unknown kind {kind!r}")
        values: list[str] = []
        reason: str | None = None
        if kind == "json-pointer":
            value, reason = read_json_pointer(claim["owner"], claim["pointer"])
            if value:
                values = matcher.findall(value)
        else:
            text = read_text(claim["owner"])
            if text is None:
                reason = f"owner does not resolve: {claim['owner']}"
            elif kind == "markdown-field":
                cell = read_field(text, claim["field"])
                if cell is None:
                    reason = f"field is absent: {claim['field']}"
                else:
                    values = matcher.findall(cell)
            else:
                block = heading_block(text, claim["section"])
                if block is None:
                    reason = f"section is absent: {claim['section']}"
                else:
                    values = matcher.findall(block)
        cited = sorted(set(values))
        unrecorded = [item for item in cited if item not in recorded]
        if reason or not cited:
            outcome = OUT_UNREADABLE
            unreadable.append(f"{claim['id']}: {reason or 'no baseline identifier was read'}")
        elif current and current[0] in cited and not unrecorded:
            outcome = OUT_AGREES
        else:
            outcome = OUT_DIVERGES
            divergences.append(f"{claim['id']}: referred to {claim['referred_to']}")
        claims.append(
            {
                "id": claim["id"],
                "claimant": claim["claimant"],
                "owner": claim["owner"],
                "kind": kind,
                "cited": cited,
                "unrecorded": unrecorded,
                "outcome": outcome,
                "referred_to": claim["referred_to"],
                "decided": False,
            }
        )
    return claims, unreadable, divergences


def measure_versions(document: dict) -> tuple[list[dict], list[str], list[str]]:
    """Version progression: an artifact above the base version must have a recorded increment."""
    sources = document["version_sources"]
    constitutional, identity, ledger = (
        sources["constitutional"],
        sources["identity"],
        sources["ledger"],
    )
    artifacts, artifact_reason = read_json_collection(
        constitutional["owner"], constitutional["collection_pointer"]
    )
    identities, identity_reason = read_json_collection(
        identity["owner"], identity["collection_pointer"]
    )
    events, ledger_reason = read_json_collection(ledger["owner"], ledger["collection_pointer"])
    # THE CORPUS REGISTRY CANNOT HOLD AN EXECUTABLE OBJECT, AND UCKP-LAW-0001 IS ONE.
    # `identity` resolves paths through 00-BOOK/DATA/artifacts.json, whose registration
    # boundary admits .md/.txt/.docx/.json and excludes .py by declaration — measured, zero
    # of its 1684 artifacts are .py. So BLN-VAL-17 asked whether the supreme law's path
    # resolved to a universal identity in the one map that structurally can never contain
    # it, and reported "no universal identity resolves for its path" about an object that
    # HAS one: engine/uckp/law.py is UCOS-ENGINE-000496 in the ledger's by_object map.
    # The second source is declared rather than hardcoded, and absence of the map is a
    # reason like any other rather than a silent empty merge.
    executable = document["version_sources"].get("executable_identity")
    executable_ids: dict[str, dict] = {}
    if executable:
        executable_ids, executable_reason = read_json_mapping(
            executable["owner"], executable["collection_pointer"]
        )
        if executable_reason:
            problems_pre = f"{executable['id']}: {executable_reason}"
        else:
            problems_pre = ""
    else:
        problems_pre = ""
    problems: list[str] = [problems_pre] if problems_pre else []
    for reason, source in (
        (artifact_reason, constitutional),
        (identity_reason, identity),
        (ledger_reason, ledger),
    ):
        if reason:
            problems.append(f"{source['id']}: {reason}")
    by_path = {
        str(entry.get(identity["path_field"])): str(entry.get(identity["id_field"]))
        for entry in identities
    }
    for path_key, record in executable_ids.items():
        by_path.setdefault(
            str(path_key), str(record.get(executable["id_field"])) if executable else ""
        )
    increments: dict[str, set[str]] = {}
    for event in events:
        if str(event.get(ledger["kind_field"])) != ledger["increment_token"]:
            continue
        increments.setdefault(str(event.get(ledger["subject_field"])), set()).add(
            str(event.get(ledger["target_field"]))
        )
    base = str(constitutional["base_version"])
    progressions: list[dict] = []
    configuration: list[str] = []
    for entry in artifacts:
        version = str(entry.get(constitutional["version_field"]) or "")
        if not version or version == base:
            continue
        subject = str(entry.get(constitutional["id_field"]))
        path = str(entry.get(constitutional["path_field"]) or "")
        universal = by_path.get(path)
        reached = universal is not None and version in increments.get(universal, set())
        progressions.append(
            {
                "id": subject,
                "version": version,
                "identity": universal,
                "increment_recorded": reached,
            }
        )
        configuration.append(f"{subject} {version}")
        if universal is None:
            problems.append(f"{subject}: no universal identity resolves for its path")
        elif not reached:
            problems.append(f"{subject}: no recorded increment reaches its version")
    return progressions, sorted(configuration), problems


def measure_lineage(document: dict) -> tuple[dict, list[str]]:
    """The constitutional lineage population, measured so a vacuous invariant is visible."""
    lineage = document["lineage_source"]
    artifacts, artifact_reason = read_json_collection(
        lineage["owner"], lineage["collection_pointer"]
    )
    relationships, relationship_reason = read_json_collection(
        lineage["owner"], lineage["relationship_pointer"]
    )
    problems: list[str] = []
    for reason in (artifact_reason, relationship_reason):
        if reason:
            problems.append(f"{lineage['id']}: {reason}")
    known = {str(entry.get(lineage["id_field"])) for entry in artifacts}
    declared = [
        (str(entry.get(lineage["id_field"])), str(entry.get(lineage["predecessor_field"])))
        for entry in artifacts
        if entry.get(lineage["predecessor_field"])
    ]
    for subject, predecessor in declared:
        if predecessor not in known:
            problems.append(f"{subject}: lineage predecessor does not resolve")
        if predecessor == subject:
            problems.append(f"{subject}: is its own lineage predecessor")
    types = {str(entry.get(lineage["relationship_type_field"])) for entry in relationships}
    located = lineage["inheritance_type_token"] in types
    if not located:
        problems.append(f"{lineage['id']}: the inheritance relationship type is not located")
    measured = {
        "owner": lineage["owner"],
        "population": len(artifacts),
        "with_predecessor": len(declared),
        "edges": sorted(f"{subject} -> {predecessor}" for subject, predecessor in declared),
        "inheritance_type_located": located,
        "vacuous": len(declared) == 0,
    }
    return measured, problems


def measure(document: dict) -> dict:  # noqa: C901 - one measurement per declared capability
    programme = document["programme"]
    roots = repository_roots()
    register = document["baseline_register"]
    scheme = document["scheme_source"]
    ceiling = document["ceiling"]

    discovered = measure_baselines(document, roots)
    baselines = discovered["baselines"]
    recorded = discovered["recorded"]
    register_text = discovered["register_text"]
    identifier_matcher = discovered["identifier_matcher"]

    # --- CAP-03 identification: the scheme is read, never restated -------
    scheme_text = read_text(scheme["owner"])
    scheme_problems: list[str] = []
    if scheme_text is None:
        scheme_problems.append(f"{scheme['id']}: owner does not resolve: {scheme['owner']}")
    elif scheme["scheme_anchor"] not in scheme_text:
        scheme_problems.append(f"{scheme['id']}: scheme anchor absent in {scheme['owner']}")
    scheme_problems.extend(
        f"{entry['id']}: does not conform to the located scheme"
        for entry in baselines
        if not entry["conformant"]
    )

    # --- CAP-04 addressability: dense, monotone, unique -------------------
    ordinal_problems: list[str] = []
    seen: set[str] = set()
    expected = int(scheme["origin_ordinal"])
    for entry in baselines:
        if entry["id"] in seen:
            ordinal_problems.append(f"{entry['id']}: duplicated in the register")
        seen.add(entry["id"])
        if entry["ordinal"] is None:
            continue
        if entry["ordinal"] != expected:
            ordinal_problems.append(f"{entry['id']}: ordinal is not dense and monotone")
        expected = entry["ordinal"] + 1

    # --- CAP-06 chain shape ----------------------------------------------
    chain, chain_problems = measure_chain(baselines)

    # --- CAP-10 currency --------------------------------------------------
    current = [entry["id"] for entry in baselines if entry["current"]]
    current_problems: list[str] = []
    if len(current) != 1:
        current_problems.append("the register does not mark exactly one current baseline")
    head_problems: list[str] = []
    if current and chain["heads"] and current[0] != chain["heads"][0]:
        head_problems.append("the current baseline is not the head of the succession chain")
    claims, claim_problems, divergences = measure_currency(
        document, recorded, current, identifier_matcher
    )

    # The current baseline's own evidence block: the subject of the criteria, chain and
    # dependency measurements below.
    current_block = ""
    if current:
        entry = next(item for item in baselines if item["id"] == current[0])
        if entry["block"] == register["owner"]:
            current_block = (
                named_block(register_text, current[0], document["succession_source"]["section_prefix"])
                or ""
            )
        else:
            current_block = read_text(entry["block"] or "") or ""

    # --- citation certification: no baseline cited but never recorded -----
    scanned = surface_files(
        document["citation_surfaces"], document.get("citation_surface_extensions") or [".md"]
    )
    citation_matcher = re.compile(rf"\b({register['id_pattern']})\b")
    unrecorded_citations: list[dict] = []
    for relative in scanned:
        if relative.startswith(OWN_PREFIX) and Path(relative).name in rendered_names():
            continue
        text = read_text(relative)
        if text is None:
            continue
        for token in sorted(set(citation_matcher.findall(text))):
            if token not in recorded:
                unrecorded_citations.append({"token": token, "surface": relative})

    # --- CAP-07 / non-inheritance / scope / elevation bindings ------------
    inheritance, inheritance_problems = bind_rules(document["inheritance_rules"])
    non_inheritance, non_inheritance_problems = bind_rules(document["non_inheritance_rules"])
    scope, scope_problems = bind_rules(document["scope_rules"])
    prohibitions, prohibition_problems = bind_rules(document["elevation_prohibitions"])

    # --- CAP-11 ceiling ---------------------------------------------------
    ceiling_text = read_text(ceiling["owner"])
    ceiling_bound = ceiling_text is not None and ceiling["anchor"] in ceiling_text
    vacancies, vacancy_reason = read_json_collection(
        ceiling["vacancy_owner"], ceiling["vacancy_pointer"]
    )
    # The vacancy corroborates the cap in EITHER of its two recorded dispositions, because
    # UCOS-RAT-002 retired VAC-01 and the located projection now records no OPEN vacancy at
    # all. A discharged obligation is not a missing one: the declaration names the tier field
    # carrying the closing act, and a tier holding it proves the question was governed rather
    # than lost. The cap itself rests on the anchor clause, which is measured separately above.
    discharges, discharge_reason = read_json_collection(
        ceiling["vacancy_owner"], ceiling["discharge_pointer"]
    )
    discharged = [
        entry for entry in discharges if str(entry.get(ceiling["discharge_field"]) or "").strip()
    ]
    ceiling_problems: list[str] = []
    if not ceiling_bound:
        ceiling_problems.append(f"{ceiling['id']}: anchor absent in {ceiling['owner']}")
    if vacancy_reason:
        ceiling_problems.append(f"{ceiling['id']}: {vacancy_reason}")
    elif discharge_reason:
        ceiling_problems.append(f"{ceiling['id']}: {discharge_reason}")
    elif not vacancies and not discharged:
        ceiling_problems.append(
            f"{ceiling['id']}: the projection records neither an open vacancy nor a located "
            "discharge, so the ceiling is unbacked"
        )
    if ceiling["disclosure_token"] not in register_text:
        ceiling_problems.append(f"{ceiling['id']}: the register does not disclose the ceiling token")

    # --- CAP-13 authority disclosure -------------------------------------
    authority_problems: list[str] = []
    if register["authority_anchor"] not in register_text:
        authority_problems.append("the register does not disclose that it holds no authority")
    if register["append_only_anchor"] not in register_text:
        authority_problems.append("the register does not declare itself append-only")
    if not str(programme["authority"]).startswith("NONE"):
        authority_problems.append("this measurement does not disclose NONE authority")

    # --- CAP-14 traceability of the located records ----------------------
    records: list[dict] = []
    record_problems: list[str] = []
    pointer_problems = list(discovered["pointer"])
    for entry in document["record_set"]["records"]:
        text = read_text(entry["owner"])
        present = text is not None and entry["anchor"] in text
        record_pointers = pointers(text or "", roots)
        unresolved = [item for item in record_pointers if not (REPO / item).exists()]
        records.append(
            {
                "id": entry["id"],
                "role": entry["role"],
                "owner": entry["owner"],
                "located": present,
                "pointers": len(record_pointers),
                "pointers_unresolved": unresolved,
            }
        )
        if not present:
            record_problems.append(f"{entry['id']}: anchor absent in {entry['owner']}")
        pointer_problems.extend(f"{entry['id']}: {item}" for item in unresolved)

    # --- CAP-08 / CAP-16 version progression and configuration ------------
    progressions, configuration, version_problems = measure_versions(document)

    # --- CAP-05 lineage ---------------------------------------------------
    lineage, lineage_problems = measure_lineage(document)

    # --- CAP-09 evolution -------------------------------------------------
    release = document["release_source"]
    release_text = read_text(release["owner"])
    release_problems: list[str] = []
    release_block = None
    if release_text is None:
        release_problems.append(f"{release['id']}: owner does not resolve: {release['owner']}")
    else:
        release_block = heading_block(release_text, release["section"])
        if release_block is None:
            release_problems.append(f"{release['id']}: the declared section is absent")
    release_matcher = re.compile(release["release_pattern"])
    claimed_releases = sorted(set(release_matcher.findall(current_block)))
    corroborated = [item for item in claimed_releases if release_block and item in release_block]
    release_problems.extend(
        f"{item}: claimed in the chain but absent from the located register"
        for item in claimed_releases
        if item not in corroborated
    )
    if current and not claimed_releases:
        release_problems.append(f"{release['id']}: the current baseline claims no chain")

    # --- CAP-18 context: the advancement criteria are discovered ----------
    criteria_problems: list[str] = []
    criteria = read_items(
        scheme_text or "", scheme["criteria_anchor"], scheme["criteria_item_prefix"]
    )
    if not criteria:
        criteria_problems.append(f"{scheme['id']}: no advancement criterion was discovered")
    normalized_block = normalize(current_block)
    corroborated_criteria: list[dict] = []
    for criterion in criteria:
        present = normalize(criterion) in normalized_block
        corroborated_criteria.append({"criterion": criterion, "corroborated": present})
        if not present:
            criteria_problems.append("a located advancement criterion is not corroborated")

    # --- CAP-19 continuation ---------------------------------------------
    continuation = document["continuation_source"]
    continuation_text = read_text(continuation["owner"])
    continuation_bound = continuation_text is not None and continuation["anchor"] in continuation_text
    continuation_problems: list[str] = []
    if not continuation_bound:
        continuation_problems.append(f"{continuation['id']}: anchor absent in {continuation['owner']}")

    # --- CAP-20 immutability of the located records -----------------------
    protected = {entry["owner"] for entry in document["record_set"]["records"]}
    write_set = {f"{OWN_PREFIX}{name}" for name in rendered_names()}
    collisions = sorted(write_set & protected)
    unprotected = sorted(
        path.relative_to(REPO).as_posix()
        for path in HERE.glob("*.md")
        if path.relative_to(REPO).as_posix() not in write_set
        and path.relative_to(REPO).as_posix() not in protected
    )
    immutability_problems = [f"{item}: is both written and a protected record" for item in collisions]
    immutability_problems += [
        f"{item}: is a record in the home that is not protected" for item in unprotected
    ]

    # Measured failure lists, keyed by validation id. This is the one place the engine names a
    # validation: measurement logic cannot be derived from data. A declared validation with no
    # measurement here is reported measured=false and satisfied=false, so it fails closed —
    # absence of a measurement is never evidence of compliance.
    findings: dict[str, list[str]] = {
        "BLN-VAL-01": (
            [f"{register['id']}: {discovered['register_reason']}"]
            if discovered["register_reason"]
            else []
        ),
        "BLN-VAL-02": sorted(set(scheme_problems)),
        "BLN-VAL-03": sorted(set(ordinal_problems)),
        "BLN-VAL-04": sorted(set(discovered["resolution"])),
        "BLN-VAL-05": sorted(set(discovered["explicit"])),
        "BLN-VAL-06": sorted(set(discovered["consistency"])),
        "BLN-VAL-07": sorted(set(chain_problems)),
        "BLN-VAL-08": sorted(set(current_problems)),
        "BLN-VAL-09": sorted(set(head_problems)),
        "BLN-VAL-10": [f"{item['token']} ({item['surface']})" for item in unrecorded_citations],
        "BLN-VAL-11": sorted(set(pointer_problems)),
        "BLN-VAL-12": sorted(set(claim_problems)),
        "BLN-VAL-13": sorted(set(inheritance_problems)),
        "BLN-VAL-14": sorted(set(non_inheritance_problems)),
        "BLN-VAL-15": sorted(set(discovered["elevation"] + prohibition_problems)),
        "BLN-VAL-16": sorted(set(ceiling_problems)),
        "BLN-VAL-17": sorted(set(version_problems)),
        "BLN-VAL-18": sorted(set(lineage_problems)),
        "BLN-VAL-19": sorted(set(release_problems)),
        "BLN-VAL-20": sorted(set(immutability_problems)),
        "BLN-VAL-21": sorted(set(criteria_problems)),
        "BLN-VAL-22": sorted(set(scope_problems)),
        "BLN-VAL-23": sorted(set(discovered["states"])),
        "BLN-VAL-24": sorted(set(authority_problems + record_problems)),
        "BLN-VAL-25": sorted(set(continuation_problems)),
        "BLN-VAL-26": [],  # filled below, once the capability measures are known
    }

    measures = {
        "baselines_registered": len(baselines),
        "records_resolved": sum(1 for entry in baselines if entry["block"]),
        "identifiers_conformant": sum(1 for entry in baselines if entry["conformant"]),
        "ordinals_addressable": len(baselines) - len(set(ordinal_problems)),
        "lineage_measured": lineage["population"],
        "successions_linked": sum(1 for entry in baselines if entry["predecessor_claimed"]),
        "inheritance_rules_bound": sum(1 for entry in inheritance if entry["bound"])
        + sum(1 for entry in non_inheritance if entry["bound"]),
        "versions_succeeded": sum(1 for entry in progressions if entry["increment_recorded"]),
        "releases_corroborated": len(corroborated),
        "currency_claims_measured": sum(
            1 for entry in claims if entry["outcome"] != OUT_UNREADABLE
        ),
        "ceiling_disclosed": 1 if ceiling_bound and not ceiling_problems else 0,
        "certification_states_read": sum(1 for entry in baselines if entry["state"]),
        "authority_disclosures": 3 - len(authority_problems),
        "pointers_resolved": sum(entry["pointers"] for entry in baselines)
        + sum(entry["pointers"] for entry in records),
        "dependency_models_resolved": len(pointers(current_block, roots)),
        "configuration_versions_read": len(configuration),
        "scope_rules_bound": sum(1 for entry in scope if entry["bound"]),
        "criteria_corroborated": sum(1 for entry in corroborated_criteria if entry["corroborated"]),
        "continuation_bound": 1 if continuation_bound else 0,
        "elevation_prohibitions_bound": sum(1 for entry in prohibitions if entry["bound"]),
    }

    capabilities = []
    for capability in document["capabilities"]:
        key = capability["measure"]
        known = key in measures
        clean = known and not any(findings.get(item) for item in CAPABILITY_GATES.get(key, ()))
        capabilities.append(
            {
                "id": capability["id"],
                "capability": capability["capability"],
                "obligation": capability["obligation"],
                "measure": key,
                "value": measures.get(key),
                "measured": known,
                "discharged": bool(clean and measures.get(key, 0) > 0),
            }
        )
    findings["BLN-VAL-26"] = [
        f"{entry['id']}: {entry['measure']}" for entry in capabilities if not entry["discharged"]
    ]

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
        "register": {
            "id": register["id"],
            "owner": register["owner"],
            "resolved": discovered["register_reason"] is None,
            "reason": discovered["register_reason"],
        },
        "scheme": {
            "id": scheme["id"],
            "owner": scheme["owner"],
            "criteria_discovered": len(criteria),
            "criteria": corroborated_criteria,
        },
        "baselines": baselines,
        "current": current,
        "chain": chain,
        "records": records,
        "inheritance_rules": inheritance,
        "non_inheritance_rules": non_inheritance,
        "scope_rules": scope,
        "elevation_prohibitions": prohibitions,
        "ceiling": {
            "id": ceiling["id"],
            "owner": ceiling["owner"],
            "bound": ceiling_bound,
            "disclosure_token": ceiling["disclosure_token"],
            "terminal_token": ceiling["terminal_token"],
            "vacancies_located": len(vacancies),
            "vacancies_discharged": len(discharged),
            "elevated": [],
        },
        "currency_claims": claims,
        "divergences_referred": sorted(divergences),
        "citation_surfaces_scanned": len(scanned),
        "unrecorded_citations": unrecorded_citations,
        "version_progressions": progressions,
        "configuration": configuration,
        "lineage": lineage,
        "evolution": {
            "owner": release["owner"],
            "claimed": claimed_releases,
            "corroborated": sorted(corroborated),
        },
        "continuation": {
            "id": continuation["id"],
            "owner": continuation["owner"],
            "bound": continuation_bound,
        },
        "immutability": {
            "write_set": sorted(write_set),
            "protected": sorted(protected),
            "intersection": collisions,
            "unprotected_records": unprotected,
            "disjoint": not collisions,
        },
        "capabilities": capabilities,
        "validations": validations,
        "counts": {
            "baselines": len(baselines),
            "records": len(records),
            "chain_length": len(chain["predecessors"]),
            "inheritance_rules": len(inheritance),
            "non_inheritance_rules": len(non_inheritance),
            "scope_rules": len(scope),
            "scope_rules_bound": measures["scope_rules_bound"],
            "currency_claims": len(claims),
            "currency_agrees": sum(1 for entry in claims if entry["outcome"] == OUT_AGREES),
            "currency_diverges": sum(1 for entry in claims if entry["outcome"] == OUT_DIVERGES),
            "surfaces_scanned": len(scanned),
            "unrecorded_citations": len(unrecorded_citations),
            "pointers": measures["pointers_resolved"],
            "version_progressions": len(progressions),
            "versions_succeeded": measures["versions_succeeded"],
            "lineage_population": lineage["population"],
            "lineage_with_predecessor": lineage["with_predecessor"],
            "releases_claimed": len(claimed_releases),
            "releases_corroborated": len(corroborated),
            "criteria": len(criteria),
            "criteria_corroborated": measures["criteria_corroborated"],
            "capabilities": len(capabilities),
            "capabilities_discharged": sum(1 for entry in capabilities if entry["discharged"]),
        },
        "blocking_failures": blocking_failures,
        "gate": gate,
        "gate_exit": 1 if blocking_failures else 0,
        "determination": (
            "BASELINE-INHERITANCE-BOUND" if gate == "OPEN" else "BASELINE-INHERITANCE-INCOMPLETE"
        ),
        "exit_criteria": list(document["exit_criteria"]),
        "findings": list(document.get("findings", [])),
    }
    model["seal_sha256"] = digest(json.dumps(model, sort_keys=True, ensure_ascii=False))
    return model



# ---------------------------------------------------------------------------
# rendering — pure: no clock, no environment, no I/O beyond the model


def table(header: list[str], rows: list[list[str]]) -> str:
    lines = ["| " + " | ".join(header) + " |", "|" + "|".join(["---"] * len(header)) + "|"]
    for row in rows:
        lines.append("| " + " | ".join(str(cell).replace("|", "\\|") for cell in row) + " |")
    return "\n".join(lines)


def yes(value: bool) -> str:
    return "YES" if value else "**NO**"


def front_matter(model: dict) -> str:
    programme = model["programme"]
    counts = model["counts"]
    rows = [
        ["PROGRAMME", f"{programme['id']} — {programme['name']}"],
        ["VERSION", programme["version"]],
        ["AUTHORITY", programme["authority"]],
        ["BASELINES REGISTERED", f"{counts['baselines']} · chain length {counts['chain_length']}"],
        ["CURRENT BASELINE", ", ".join(f"`{item}`" for item in model["current"]) or "**none**"],
        ["CHAIN", f"origins {len(model['chain']['origins'])} · heads {len(model['chain']['heads'])} · acyclic {yes(model['chain']['acyclic'])}"],
        ["INHERITANCE RULES BOUND", f"{counts['inheritance_rules']} + {counts['non_inheritance_rules']} non-inheritance"],
        ["CURRENCY CLAIMS", f"{counts['currency_claims']} · {counts['currency_agrees']} agree · {counts['currency_diverges']} referred"],
        ["CITATIONS", f"{counts['unrecorded_citations']} unrecorded over {counts['surfaces_scanned']} surfaces"],
        ["POINTERS", counts["pointers"]],
        ["VERSION PROGRESSION", f"{counts['versions_succeeded']}/{counts['version_progressions']} recorded"],
        ["CONSTITUTIONAL LINEAGE", f"{counts['lineage_with_predecessor']}/{counts['lineage_population']} artifacts record a predecessor"],
        ["EVOLUTION CHAIN", f"{counts['releases_corroborated']}/{counts['releases_claimed']} corroborated"],
        ["ADVANCEMENT CRITERIA", f"{counts['criteria_corroborated']}/{counts['criteria']} corroborated"],
        ["RECORD IMMUTABILITY", f"write ∩ record = {len(model['immutability']['intersection'])} · disjoint {yes(model['immutability']['disjoint'])}"],
        ["CAPABILITIES DISCHARGED", f"{counts['capabilities_discharged']}/{counts['capabilities']}"],
        ["GATE", model["gate"]],
        ["DETERMINATION", model["determination"]],
        ["SEAL (sha256)", model["seal_sha256"]],
        ["GENERATED BY", "baseline_engine.py — regenerated, never hand-authored"],
    ]
    return table(["Field", "Value"], rows) + "\n\n> " + model["programme"]["disclosure"]


def render(model: dict) -> dict[str, str]:  # noqa: C901 - one page per measured concern
    pages: dict[str, str] = {}
    programme = model["programme"]

    pages["00-BASELINE-INHERITANCE-DASHBOARD.md"] = "\n".join(
        [
            f"# {programme['id']} — {programme['name']} · Dashboard",
            "",
            front_matter(model),
            "",
            "## Capability discharge",
            "",
            table(
                ["Capability", "Obligation", "Measure", "Value", "Discharged"],
                [
                    [
                        f"`{entry['id']}` {entry['capability']}",
                        entry["obligation"],
                        f"`{entry['measure']}`",
                        entry["value"],
                        yes(entry["discharged"]),
                    ]
                    for entry in model["capabilities"]
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

    pages["01-SUCCESSION-AND-ADDRESSABILITY-REGISTER.md"] = "\n".join(
        [
            f"# {programme['id']} · Succession and Addressability",
            "",
            "Every row below is DISCOVERED from the located register named in the register row.",
            "No baseline is recorded, advanced or certified by this measurement.",
            "",
            table(
                ["Register", "Owner", "Resolves"],
                [
                    [
                        f"`{model['register']['id']}`",
                        f"`{model['register']['owner']}`",
                        yes(model["register"]["resolved"])
                        if model["register"]["resolved"]
                        else f"**NO** — {model['register']['reason']}",
                    ]
                ],
            ),
            "",
            "## Recorded baselines",
            "",
            table(
                ["Row", "Baseline", "Ordinal", "Scheme", "Commit", "Branch", "Date", "State", "Current"],
                [
                    [
                        entry["row"],
                        f"`{entry['id']}`",
                        entry["ordinal"] if entry["ordinal"] is not None else "**none**",
                        yes(entry["conformant"]),
                        yes(entry["commit_recorded"]),
                        yes(entry["branch_recorded"]),
                        yes(entry["date_recorded"]),
                        entry["state"],
                        "**YES**" if entry["current"] else "no",
                    ]
                    for entry in model["baselines"]
                ],
            ),
            "",
            "## Succession",
            "",
            "The meta-constitution requires inheritance to be EXPLICIT and prohibits implicit",
            "inheritance from a containing programme, phase or directory. Row order alone is",
            "therefore insufficient: a non-origin baseline must RECORD its predecessor. Both the",
            "explicit claim and the structural order are measured, and a disagreement between them",
            "is a failure rather than a resolution in favour of either.",
            "",
            table(
                ["Baseline", "Origin", "Explicit predecessor", "Structurally preceding", "Evidence block", "Pointers", "Unresolved"],
                [
                    [
                        f"`{entry['id']}`",
                        "YES" if entry["origin"] else "no",
                        ", ".join(f"`{item}`" for item in entry["predecessor_claimed"]) or "—",
                        f"`{entry['predecessor_structural']}`" if entry["predecessor_structural"] else "—",
                        f"`{entry['block']}`" if entry["block"] else "**none**",
                        entry["pointers"],
                        len(entry["pointers_unresolved"]),
                    ]
                    for entry in model["baselines"]
                ],
            ),
            "",
            "## Chain shape",
            "",
            table(
                ["Property", "Value"],
                [
                    ["Origins", ", ".join(f"`{item}`" for item in model["chain"]["origins"]) or "—"],
                    ["Heads", ", ".join(f"`{item}`" for item in model["chain"]["heads"]) or "—"],
                    ["Acyclic", yes(model["chain"]["acyclic"])],
                    [
                        "Edges",
                        ", ".join(
                            f"`{child}` → `{parent}`"
                            for child, parent in sorted(model["chain"]["predecessors"].items())
                            if parent
                        )
                        or "—",
                    ],
                ],
            ),
            "",
            "## Protected records",
            "",
            "These are the append-only records this measurement may never write. The write set is",
            "proved disjoint from them, and every record present in the home is proved to be a",
            "member of the protected set.",
            "",
            table(
                ["Record", "Role", "Owner", "Located", "Pointers", "Unresolved"],
                [
                    [
                        f"`{entry['id']}`",
                        entry["role"],
                        f"`{entry['owner']}`",
                        yes(entry["located"]),
                        entry["pointers"],
                        len(entry["pointers_unresolved"]),
                    ]
                    for entry in model["records"]
                ],
            ),
            "",
            table(
                ["Immutability", "Value"],
                [
                    ["Write set", ", ".join(f"`{item}`" for item in model["immutability"]["write_set"])],
                    ["Protected set", ", ".join(f"`{item}`" for item in model["immutability"]["protected"])],
                    ["Intersection", ", ".join(f"`{item}`" for item in model["immutability"]["intersection"]) or "**empty**"],
                    ["Records in the home outside the protected set", ", ".join(f"`{item}`" for item in model["immutability"]["unprotected_records"]) or "**none**"],
                    ["Disjoint", yes(model["immutability"]["disjoint"])],
                ],
            ),
            "",
        ]
    )

    pages["02-INHERITANCE-AND-NON-INHERITANCE-REGISTER.md"] = "\n".join(
        [
            f"# {programme['id']} · Inheritance and Non-Inheritance",
            "",
            "What a successor inherits, and what it never inherits, are both constitutional. Each",
            "rule below binds to the located clause that states it, and the clause text is verified",
            "present in its owner. A rule whose anchor is absent is a binding failure, not a silent",
            "pass. No rule is restated here: only located, and bound.",
            "",
            "## Inheritance rules",
            "",
            table(
                ["Rule", "Obligation", "Located in", "Bound"],
                [
                    [f"`{entry['id']}`", entry["rule"], f"`{entry['owner']}`", yes(entry["bound"])]
                    for entry in model["inheritance_rules"]
                ],
            ),
            "",
            "## Non-inheritance rules",
            "",
            "Standing, ratification, finality and authority are never inherited. This was the",
            "wholly unmeasured half of the concept.",
            "",
            table(
                ["Rule", "Prohibition", "Located in", "Bound"],
                [
                    [f"`{entry['id']}`", entry["rule"], f"`{entry['owner']}`", yes(entry["bound"])]
                    for entry in model["non_inheritance_rules"]
                ],
            ),
            "",
            "## Scope",
            "",
            table(
                ["Rule", "Bound of a baseline", "Located in", "Bound"],
                [
                    [f"`{entry['id']}`", entry["rule"], f"`{entry['owner']}`", yes(entry["bound"])]
                    for entry in model["scope_rules"]
                ],
            ),
            "",
            "## Elevation prohibitions and the ratification ceiling",
            "",
            "The one thing a baseline measurement must never do is raise the standing of what it",
            "measures. No recorded baseline carries the terminal finality token, and this",
            "measurement confers no state on any baseline.",
            "",
            table(
                ["Prohibition", "Rule", "Located in", "Bound"],
                [
                    [f"`{entry['id']}`", entry["rule"], f"`{entry['owner']}`", yes(entry["bound"])]
                    for entry in model["elevation_prohibitions"]
                ],
            ),
            "",
            table(
                ["Ceiling", "Value"],
                [
                    ["Owner", f"`{model['ceiling']['owner']}`"],
                    ["Clause bound", yes(model["ceiling"]["bound"])],
                    ["Disclosure token", f"`{model['ceiling']['disclosure_token']}`"],
                    ["Terminal token (prohibited in a record)", f"`{model['ceiling']['terminal_token']}`"],
                    ["Vacancies located", model["ceiling"]["vacancies_located"]],
                    ["Vacancies discharged", model["ceiling"]["vacancies_discharged"]],
                    ["Baselines elevated by this measurement", ", ".join(model["ceiling"]["elevated"]) or "**none**"],
                ],
            ),
            "",
        ]
    )

    pages["03-CURRENCY-AND-CITATION-REGISTER.md"] = "\n".join(
        [
            f"# {programme['id']} · Currency and Citation",
            "",
            "A register other than the baseline register may name a baseline as the one in force.",
            "Where such a claim and the located register disagree, this measurement neither",
            "silences the claim nor overrides the register: it reads both, cites both, and reports",
            "a referred outcome for the claim owner to dispose of. No claimant is edited here, and",
            "every claimant is named in the programme's forbidden write prefixes so that it cannot",
            "be.",
            "",
            table(
                ["Claim", "Claimant", "Owner", "Kind", "Cites", "Unrecorded", "Outcome", "Referred to", "Decided here"],
                [
                    [
                        f"`{entry['id']}`",
                        entry["claimant"],
                        f"`{entry['owner']}`",
                        entry["kind"],
                        ", ".join(f"`{item}`" for item in entry["cited"]) or "—",
                        ", ".join(f"`{item}`" for item in entry["unrecorded"]) or "—",
                        entry["outcome"],
                        f"`{entry['referred_to']}`",
                        "no",
                    ]
                    for entry in model["currency_claims"]
                ],
            ),
            "",
            "## Divergences referred",
            "",
            (
                "\n".join(f"- {item}" for item in model["divergences_referred"])
                if model["divergences_referred"]
                else "None. Every located currency claim agrees with the register that records currency."
            ),
            "",
            "## Citation certification",
            "",
            f"Surfaces scanned: **{model['counts']['surfaces_scanned']}**. Every baseline-shaped",
            "reference in the declared surfaces must resolve to a recorded baseline: this is the",
            "machine form of *no baseline shall be cited that was never recorded*.",
            "",
            (
                table(
                    ["Token", "Surface"],
                    [[f"`{item['token']}`", f"`{item['surface']}`"] for item in model["unrecorded_citations"]],
                )
                if model["unrecorded_citations"]
                else "No baseline is cited anywhere in the declared surfaces that the register does not record."
            ),
            "",
        ]
    )

    pages["04-VERSION-LINEAGE-AND-EVOLUTION-REGISTER.md"] = "\n".join(
        [
            f"# {programme['id']} · Version Progression, Lineage and Evolution",
            "",
            "## Version progression",
            "",
            "The constitutional programme requires that any change occur only through the amendment",
            "model and increment the version. Nothing measured that the increment was RECORDED.",
            "Three located registers are read against each other: the constitutional register that",
            "records the version in force, the artifact register that maps a path to its universal",
            "identity, and the change ledger that records the increment event.",
            "",
            table(
                ["Artifact", "Recorded version", "Universal identity", "Increment recorded"],
                [
                    [
                        f"`{entry['id']}`",
                        entry["version"],
                        f"`{entry['identity']}`" if entry["identity"] else "**none**",
                        yes(entry["increment_recorded"]),
                    ]
                    for entry in model["version_progressions"]
                ],
            )
            or "No constitutional artifact stands above the base version.",
            "",
            "## Configuration in force at the current baseline",
            "",
            (
                "\n".join(f"- `{item}`" for item in model["configuration"])
                if model["configuration"]
                else "Every constitutional artifact stands at the base version."
            ),
            "",
            "## Constitutional lineage",
            "",
            "The meta-constitution requires every lineage predecessor to resolve to a present",
            "artifact, and the located validator checks exactly that. The invariant is satisfiable",
            "vacuously when no artifact records a predecessor, and a vacuously satisfied invariant",
            "is indistinguishable from an enforced one unless the population is measured. This",
            "measurement reports the population. It does not populate the field.",
            "",
            table(
                ["Property", "Value"],
                [
                    ["Owner", f"`{model['lineage']['owner']}`"],
                    ["Registered artifacts", model["lineage"]["population"]],
                    ["Artifacts recording a predecessor", model["lineage"]["with_predecessor"]],
                    ["Inheritance relationship type located", yes(model["lineage"]["inheritance_type_located"])],
                    ["Invariant vacuously satisfied", "**YES**" if model["lineage"]["vacuous"] else "no"],
                    ["Edges", ", ".join(f"`{item}`" for item in model["lineage"]["edges"]) or "—"],
                ],
            ),
            "",
            "## Evolution chain",
            "",
            f"Owner: `{model['evolution']['owner']}`. The releases the current baseline claims in",
            "its chain must be recorded in the located evolution register. Nothing about the",
            "release scheme, the release states or the release ordering is asserted here, because",
            "none of it belongs to this owner.",
            "",
            table(
                ["Release claimed by the current baseline", "Recorded in the located register"],
                [
                    [f"`{item}`", yes(item in model["evolution"]["corroborated"])]
                    for item in model["evolution"]["claimed"]
                ],
            )
            or "The current baseline claims no evolution chain.",
            "",
            "## Advancement criteria",
            "",
            f"Discovered from `{model['scheme']['owner']}`: **{model['scheme']['criteria_discovered']}**.",
            "Each criterion is read from the located scheme owner and corroborated in the current",
            "baseline's own evidence block. A criterion the owner adds is measured on the next run.",
            "",
            table(
                ["Criterion", "Corroborated in the current baseline"],
                [[entry["criterion"], yes(entry["corroborated"])] for entry in model["scheme"]["criteria"]],
            )
            or "No advancement criterion was discovered.",
            "",
            "## Continuation",
            "",
            "A baseline is complete for the scope it certifies and is never a claim of completeness",
            "beyond it.",
            "",
            table(
                ["Continuation", "Owner", "Bound"],
                [
                    [
                        f"`{model['continuation']['id']}`",
                        f"`{model['continuation']['owner']}`",
                        yes(model["continuation"]["bound"]),
                    ]
                ],
            ),
            "",
        ]
    )

    pages["05-VALIDATION-REPORT.md"] = "\n".join(
        [
            f"# {programme['id']} · Validation Report",
            "",
            "Every dimension is measured. A dimension declared and not measured is reported",
            "`measured = NO` and fails closed: absence of a measurement is never evidence of",
            "compliance.",
            "",
            table(
                ["Dimension", "Obligation", "Blocking", "Measured", "Satisfied", "Failures"],
                [
                    [
                        f"`{entry['id']}` {entry['dimension']}",
                        entry["obligation"],
                        yes(entry["blocking"]) if entry["blocking"] else "no",
                        yes(entry["measured"]),
                        yes(entry["satisfied"]),
                        entry["failure_count"],
                    ]
                    for entry in model["validations"]
                ],
            ),
            "",
            "## Measured failures",
            "",
            (
                "\n".join(
                    f"### `{entry['id']}` {entry['dimension']}\n\n"
                    + "\n".join(f"- {item}" for item in entry["failures"])
                    + "\n"
                    for entry in model["validations"]
                    if entry["failures"]
                )
                or "None."
            ),
            "",
        ]
    )

    pages["06-CERTIFICATION-REPORT.md"] = "\n".join(
        [
            f"# {programme['id']} · Certification Report",
            "",
            front_matter(model),
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
                ["Finding", "Class", "Disposition", "Blocking", "Title"],
                [
                    [
                        f"`{item['id']}`",
                        item["class"],
                        item["disposition"],
                        "YES" if item.get("blocking") else "no",
                        item["title"],
                    ]
                    for item in model["findings"]
                ],
            ),
            "",
            "CERTIFIED-PROVISIONAL. This measurement holds no certification authority, no",
            "ratification authority and no freeze authority: it registers, resolves, validates and",
            "reports the baselines the repository has already recorded. Where this measurement and",
            "a located record differ, **the located record governs**.",
            "",
        ]
    )
    return pages


def write_registers(model: dict) -> list[str]:
    written = []
    for name, body in sorted(render(model).items()):
        target = HERE / name
        target.write_text(body if body.endswith("\n") else body + "\n", encoding="utf-8")
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
    seen: set[str] = set()
    sections = (
        "capabilities",
        "inheritance_rules",
        "non_inheritance_rules",
        "scope_rules",
        "elevation_prohibitions",
        "currency_claims",
        "validations",
        "exit_criteria",
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
    for entry in document["record_set"]["records"]:
        identifier = entry.get("id")
        if identifier in seen:
            problems.append(f"record_set: duplicate id {identifier}")
        seen.add(identifier)
    measures = [entry["measure"] for entry in document["capabilities"]]
    problems.extend(
        f"capabilities: duplicate measure {item}"
        for item in sorted({item for item in measures if measures.count(item) > 1})
    )
    for section in ("inheritance_rules", "non_inheritance_rules", "scope_rules", "elevation_prohibitions"):
        for entry in document[section]:
            if not (REPO / entry["owner"]).is_file():
                problems.append(f"{entry['id']}: owner does not resolve: {entry['owner']}")
    for entry in document["record_set"]["records"]:
        if not (REPO / entry["owner"]).is_file():
            problems.append(f"{entry['id']}: owner does not resolve: {entry['owner']}")
        if not str(entry.get("anchor", "")).strip():
            problems.append(f"{entry['id']}: no anchor recorded")
    for key in (
        "baseline_register",
        "scheme_source",
        "release_source",
        "lineage_source",
        "ceiling",
        "certification_source",
        "continuation_source",
    ):
        owner = document[key]["owner"]
        if not (REPO / owner).is_file():
            problems.append(f"{key}: owner does not resolve: {owner}")
    for name, source in document["version_sources"].items():
        if not (REPO / source["owner"]).is_file():
            problems.append(f"version_sources.{name}: owner does not resolve: {source['owner']}")
    if not (REPO / document["ceiling"]["vacancy_owner"]).is_file():
        problems.append("ceiling: vacancy owner does not resolve")
    for claim in document["currency_claims"]:
        if claim.get("kind") not in CLAIM_KINDS:
            problems.append(f"{claim['id']}: unknown kind {claim.get('kind')!r}")
        if not (REPO / claim["owner"]).is_file():
            problems.append(f"{claim['id']}: owner does not resolve: {claim['owner']}")
        if not (REPO / claim["referred_to"]).exists():
            problems.append(f"{claim['id']}: referral target does not resolve")
    for surface in document["citation_surfaces"]:
        if not (REPO / surface).exists():
            problems.append(f"citation_surfaces: does not resolve: {surface}")
    # A claimant this measurement could write is a claimant it could silently reconcile.
    forbidden = tuple(document["programme"]["forbidden_write_prefixes"])
    for claim in document["currency_claims"]:
        if claim["owner"].startswith(OWN_PREFIX):
            continue
        if not any(claim["owner"].startswith(prefix) for prefix in forbidden):
            problems.append(f"{claim['id']}: claimant is not protected by a forbidden write prefix")
    return problems


def check_no_enumeration(document: dict) -> list[str]:
    """No discovered identity may appear as a literal in this engine's source."""
    source = Path(__file__).read_text(encoding="utf-8")
    model = measure(document)
    leaked: list[str] = []
    for entry in model["baselines"]:
        if re.search(rf"\b{re.escape(entry['id'])}\b", source):
            leaked.append(f"baseline {entry['id']}")
        if entry["ordinal"] is not None and re.search(
            rf"\"{entry['ordinal']:03d}\"", source
        ):  # pragma: no cover - defensive
            leaked.append(f"ordinal of {entry['id']}")
    for item in model["evolution"]["claimed"]:
        if item in source:
            leaked.append(f"release {item}")
    for entry in model["version_progressions"]:
        if entry["identity"] and entry["identity"] in source:
            leaked.append(f"identity {entry['identity']}")
    return sorted(set(leaked))


def check_write_scope(document: dict) -> list[str]:
    problems: list[str] = []
    for name in rendered_names():
        try:
            (HERE / name).resolve().relative_to(HERE)
        except ValueError:  # pragma: no cover - defensive
            problems.append(name)
    rendered = set(render(measure(document)))
    if rendered != set(PAGES):
        problems.append("the renderer does not produce exactly the declared page set")
    for prefix in document["programme"]["forbidden_write_prefixes"]:
        if OWN_PREFIX.startswith(prefix):
            problems.append(f"own home falls inside a forbidden prefix: {prefix}")
    return problems


def check_determinism(document: dict) -> list[str]:
    first, second = render(measure(document)), render(measure(document))
    problems = sorted(name for name in first if first[name] != second.get(name))
    if measure(document)["seal_sha256"] != measure(document)["seal_sha256"]:  # pragma: no cover
        problems.append("the seal is not stable across two measurements")
    return problems


def check_knowledge_once(document: dict) -> list[str]:
    """No baseline may be DEFINED in this declaration; every one must be discovered."""
    problems: list[str] = []
    raw = DECLARATION.read_text(encoding="utf-8")
    model = measure(document)
    for entry in model["baselines"]:
        if re.search(rf"\"{re.escape(entry['id'])}\"", raw) or entry["id"] in raw:
            problems.append(f"declaration names baseline {entry['id']}")
    for item in model["evolution"]["claimed"]:
        if item in raw:
            problems.append(f"declaration names release {item}")
    if not model["baselines"]:
        problems.append("no baseline was discovered from the located register")
    return problems


def check_record_immutability(document: dict) -> list[str]:
    """MANDATORY. write_set ∩ canonical_record_set = ∅, and every record is protected.

    The first half proves this measurement cannot write an append-only record. The second half
    proves the protected set cannot be quietly narrowed: a record present in the programme home
    that is neither written nor declared protected is unprotected, and fails closed.
    """
    model = measure(document)
    immutability = model["immutability"]
    problems = [
        f"write set intersects the canonical record set: {item}"
        for item in immutability["intersection"]
    ]
    problems += [
        f"record in the home is outside the protected set: {item}"
        for item in immutability["unprotected_records"]
    ]
    for entry in model["records"]:
        if not entry["located"]:
            problems.append(f"{entry['id']}: protected record is absent or its anchor moved")
    if not immutability["protected"]:
        problems.append("no record is protected, so immutability is unmeasured")
    return problems


def check_no_elevation(document: dict) -> list[str]:
    """This measurement must never raise the standing of what it measures."""
    model = measure(document)
    problems: list[str] = []
    terminal = str(model["ceiling"]["terminal_token"]).upper()
    for entry in model["baselines"]:
        if terminal and terminal in entry["state"].upper():
            problems.append(f"{entry['id']}: the register records the terminal finality token")
    if model["ceiling"]["elevated"]:
        problems.append("this measurement reports a baseline as elevated")
    for entry in model["currency_claims"]:
        if entry["decided"]:
            problems.append(f"{entry['id']}: a currency divergence was decided rather than referred")
    if not model["ceiling"]["bound"]:
        problems.append("the ratification ceiling is not bound, so no standing may be reported")
    if not str(model["programme"]["authority"]).startswith("NONE"):
        problems.append("this measurement claims an authority")
    return problems


GUARDS = {
    "check-declaration": check_declaration,
    "check-no-enumeration": check_no_enumeration,
    "check-write-scope": check_write_scope,
    "check-determinism": check_determinism,
    "check-knowledge-once": check_knowledge_once,
    "check-record-immutability": check_record_immutability,
    "check-no-elevation": check_no_elevation,
}


# ---------------------------------------------------------------------------
# cli


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(add_help=True, description=__doc__.splitlines()[0])
    parser.add_argument("--render", action="store_true", help="regenerate the registers")
    parser.add_argument("--gate", action="store_true", help="fail-closed baseline gate")
    parser.add_argument("--quiet", action="store_true")
    for name in GUARDS:
        parser.add_argument(f"--{name}", action="store_true")
    args = parser.parse_args(argv)

    try:
        document = load_declaration()
    except FailClosed as exc:
        print(f"BASELINE-001 ABORT: {exc}", file=sys.stderr)
        return 2

    selected = [name for name in GUARDS if getattr(args, name.replace("-", "_"))]
    if selected:
        failed = False
        for name in selected:
            try:
                problems = GUARDS[name](document)
            except FailClosed as exc:
                print(f"BASELINE-001 ABORT: {exc}", file=sys.stderr)
                return 2
            if problems:
                failed = True
                print(f"BASELINE-001 {name}: FAIL ({len(problems)})", file=sys.stderr)
                for problem in problems[:40]:
                    print(f"  - {problem}", file=sys.stderr)
            else:
                print(f"BASELINE-001 {name}: PASS")
        return 1 if failed else 0

    try:
        model = measure(document)
    except FailClosed as exc:
        print(f"BASELINE-001 ABORT: {exc}", file=sys.stderr)
        return 2

    written = write_registers(model)
    counts = model["counts"]
    if not args.quiet:
        print(
            f"BASELINE-001: {model['determination']} | baselines={counts['baselines']} "
            f"| chain={counts['chain_length']}(1 origin,{len(model['chain']['heads'])} head) "
            f"| current={','.join(model['current']) or 'none'} "
            f"| inheritance={counts['inheritance_rules']}+{counts['non_inheritance_rules']} "
            f"| currency={counts['currency_agrees']}agree/{counts['currency_diverges']}referred "
            f"| citations={counts['unrecorded_citations']}unrecorded/{counts['surfaces_scanned']} "
            f"| versions={counts['versions_succeeded']}/{counts['version_progressions']} "
            f"| releases={counts['releases_corroborated']}/{counts['releases_claimed']} "
            f"| criteria={counts['criteria_corroborated']}/{counts['criteria']} "
            f"| immutable={str(model['immutability']['disjoint']).lower()} "
            f"| gate={model['gate']} | seal={model['seal_sha256'][:16]}"
        )
        print(f"wrote {len(written)} artifacts to {HERE.relative_to(REPO).as_posix()}")
        for entry in model["validations"]:
            if entry["blocking"] and not entry["satisfied"]:
                print(
                    f"  BLOCKING {entry['id']} {entry['dimension']}: {entry['failure_count']}",
                    file=sys.stderr,
                )
                for failure in entry["failures"][:10]:
                    print(f"    - {failure}", file=sys.stderr)

    if args.gate:
        return model["gate_exit"]
    return 0


if __name__ == "__main__":
    sys.exit(main())
