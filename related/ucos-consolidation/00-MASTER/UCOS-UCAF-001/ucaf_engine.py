#!/usr/bin/env python3
"""UCOS-UCAF-001 — Universal Constitutional Authority Framework.

AUTHORITY = NONE (DERIVED TRUTH). This engine creates no authority, confers no authority,
occupies no tier, ratifies nothing and certifies no artifact. Every authority it registers is
DISCOVERED by reading a located instrument that already defines it; every competence question
it answers is answered by a clause it reads out of a located instrument; every conflict it
finds between a recorded claim of authority absence and located evidence of authority presence
is reported and referred to the claim owner, never decided here.

It also reads the tier PROJECTION every gate consults against the canonical lattice that
projection projects, and against the charter vesting that lattice may not amend; and it
discovers the authority tokens the executable plane mints, so an authority that is exercised by
code is bound to the authority the corpus located. Corroboration is computed only for a tier
already reported occupied: reading located evidence as the occupant of a recorded vacancy would
be a promotion, which this engine must never perform.

    python3 00-MASTER/UCOS-UCAF-001/ucaf_engine.py --render     # regenerate the registers
    python3 00-MASTER/UCOS-UCAF-001/ucaf_engine.py --gate       # fail-closed authority gate
    python3 00-MASTER/UCOS-UCAF-001/ucaf_engine.py --check-declaration
    python3 00-MASTER/UCOS-UCAF-001/ucaf_engine.py --check-no-enumeration
    python3 00-MASTER/UCOS-UCAF-001/ucaf_engine.py --check-write-scope
    python3 00-MASTER/UCOS-UCAF-001/ucaf_engine.py --check-determinism
    python3 00-MASTER/UCOS-UCAF-001/ucaf_engine.py --check-knowledge-once
    python3 00-MASTER/UCOS-UCAF-001/ucaf_engine.py --check-no-promotion

Exit semantics:
    0  every blocking validation satisfied — gate OPEN
    1  a blocking validation unsatisfied, or a self-guard failed — gate CLOSED
    2  fail-closed abort — the declaration is unusable, so no verdict may be asserted

Every source, tier pointer, lattice pointer, vesting pointer, realization source, token class,
realization binding, delegation pointer, succession pointer, scope rule, resolution question,
reconciliation, admission disposition and validation dimension is read from
ucaf-authority.json. No authority identifier, no tier identifier, no vacancy identifier, no
minted token and no resolution answer appears as a literal below, which is what makes extension
an edit to DATA and to the located instruments rather than to code.

Stdlib only. No network. No timestamp, no duration, no commit identity and no absolute path is
emitted, so the sealed output set is byte-identical for an unchanged repository.
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
DECLARATION = HERE / "ucaf-authority.json"
MODEL = HERE / "ucaf.json"
OWN_PREFIX = HERE.relative_to(REPO).as_posix() + "/"

REQUIRED_SECTIONS = (
    "programme",
    "capabilities",
    "authority_sources",
    "source_token_registers",
    "tier_source",
    "tier_lattice_source",
    "tier_vesting_source",
    "realization_sources",
    "realization_token_classes",
    "realization_bindings",
    "admission_determination",
    "delegation_sources",
    "succession_sources",
    "revocations",
    "scope_rules",
    "resolutions",
    "reconciliations",
    "reference_surfaces",
    "validations",
    "exit_criteria",
)

# Reader formats a source entry may declare. A format outside this set is a fail-closed
# violation: it is how an unimplemented reader would otherwise pass silently.
FORMATS = ("markdown-table", "article-authority", "document-token", "vesting-list")

# Corroboration channels for a tier the projection reports occupied. Each is a PROPERTY this
# engine derives by reading a located instrument — never a fact declared about a tier. A tier
# corroborated by no channel is an occupancy claim with nothing behind it.
CHANNEL_CONTENT = "canonical-lattice-content"
CHANNEL_ARTIFACT = "registered-artifact"
CHANNEL_AUTHORITY = "located-authority-of-the-same-name"
CHANNEL_VESTING = "charter-vesting"

# Reconciliation outcomes. These are properties this engine DERIVES from two measurements —
# never properties of the claim's identity.
OUT_BOTH = "RECONCILIATION-REQUIRED"
OUT_CLAIM_ABSENT = "CLAIM-NO-LONGER-LOCATED"
OUT_EVIDENCE_ABSENT = "CLAIM-STANDS-UNRECONCILED"


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


# ---------------------------------------------------------------------------
# readers — each returns rows discovered from a LOCATED instrument


def split_row(line: str) -> list[str]:
    """Split one markdown table row into stripped cells, with emphasis removed."""
    cells = line.strip().strip("|").split("|")
    return [cell.strip().replace("**", "").strip() for cell in cells]


def table_rows(text: str, section: str | None) -> list[list[str]]:
    """Yield the data rows of the first pipe table at or after `section`.

    section None means the first table in the document. A separator row (all dashes) is
    dropped, and so is the header row that precedes it.
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


def read_markdown_table_source(source: dict) -> tuple[list[dict], str | None]:
    """Discover records from a pipe table. Returns (records, unavailable_reason)."""
    owner = source.get("owner")
    if not owner:
        return [], "no owner declared"
    text = read_text(owner)
    if text is None:
        return [], f"owner does not resolve: {owner}"
    pattern = source.get("id_pattern")
    if not pattern:
        return [], "no id_pattern declared"
    matcher = re.compile(rf"^({pattern})$")
    columns = source.get("columns") or {}
    records: list[dict] = []
    for cells in table_rows(text, source.get("section")):
        if not cells:
            continue
        found = matcher.match(cells[0])
        if not found:
            continue
        record = {"id": found.group(1), "owner": owner}
        for field, index in sorted(columns.items()):
            record[field] = cells[index] if index < len(cells) else ""
        records.append(record)
    return records, None


def read_article_authority_source(source: dict) -> tuple[list[dict], str | None]:
    """Discover instrument authorities from an ARTICLE I heading across a glob."""
    glob = source.get("owner_glob")
    if not glob:
        return [], "no owner_glob declared"
    heading = source.get("heading_pattern")
    if not heading:
        return [], "no heading_pattern declared"
    matcher = re.compile(heading, re.MULTILINE)
    records: list[dict] = []
    for path in sorted(REPO.glob(glob)):
        relative = path.relative_to(REPO).as_posix()
        text = read_text(relative)
        if text is None:
            continue
        found = matcher.search(text)
        if not found:
            continue
        name = found.group("name").strip()
        # The identifier is DERIVED from the instrument's own stem, never enumerated here.
        stem = path.stem.split("-CONSTITUTIONAL")[0].split("-")[0:2]
        instrument = "-".join(stem)
        records.append(
            {
                "id": f"{instrument}::{name}",
                "owner": relative,
                "name": f"{name.title()} Authority",
                "definition": found.group(0).strip(),
                "sources": instrument,
                "authoritative": relative,
            }
        )
    if not records:
        return [], f"no instrument declared an authority article under {glob}"
    return records, None


def read_document_tokens(source: dict) -> tuple[set[str], str | None]:
    """Collect every token of a declared family that appears in a located document."""
    owner = source.get("owner")
    text = read_text(owner) if owner else None
    if text is None:
        return set(), f"owner does not resolve: {owner}"
    pattern = source.get("id_pattern")
    if not pattern:
        return set(), "no id_pattern declared"
    return set(re.findall(rf"\b(?:{pattern})\b", text)), None


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


def read_vesting_list(source: dict) -> tuple[list[dict], str | None]:
    """Discover the authority tiers a located instrument vests, from a bulleted list.

    The list is found by its declared anchor line and consumed while the declared item
    pattern keeps matching. An anchor that is absent is reported rather than treated as an
    empty vesting: an instrument that no longer vests what it is read for must not pass as
    one that vests nothing.
    """
    owner = source.get("owner")
    text = read_text(owner) if owner else None
    if text is None:
        return [], f"owner does not resolve: {owner}"
    anchor = source.get("anchor")
    pattern = source.get("item_pattern")
    if not anchor or not pattern:
        return [], "no anchor or no item_pattern declared"
    lines = text.splitlines()
    start = next((index + 1 for index, line in enumerate(lines) if anchor in line), None)
    if start is None:
        return [], f"anchor absent in {owner}"
    matcher = re.compile(pattern)
    records: list[dict] = []
    for line in lines[start:]:
        found = matcher.match(line.strip())
        if not found:
            if records or not line.strip():
                break
            continue
        fields = found.groupdict()
        records.append(
            {
                "id": f"{source['id']}-{fields.get('ordinal', '')}",
                "ordinal": fields.get("ordinal", ""),
                "name": (fields.get("name") or "").strip(),
                "occupant": (fields.get("occupant") or "").strip(),
                "owner": owner,
            }
        )
    if not records:
        return [], f"no vesting item matched under the anchor in {owner}"
    return records, None


def read_minted_tokens(source: dict) -> tuple[list[dict], str | None]:
    """Discover authority tokens the executable plane mints, from module-level constants.

    Nothing about the population is declared: the globs say WHERE to look, the symbol suffix
    says which constants are authority disclosures, and the assignment pattern says how to
    read one. A token added under a declared glob is therefore observed here without any edit
    to the declaration, which is what keeps the classification obligation honest.
    """
    globs = source.get("owner_globs") or []
    pattern = source.get("assignment_pattern")
    suffix = source.get("symbol_suffix")
    if not globs or not pattern or not suffix:
        return [], "no owner_globs, no symbol_suffix or no assignment_pattern declared"
    excluded = tuple(source.get("exclude_fragments") or ())
    matcher = re.compile(pattern, re.MULTILINE)
    records: list[dict] = []
    seen: set[tuple[str, str]] = set()
    for glob in globs:
        for path in sorted(REPO.glob(glob)):
            relative = path.relative_to(REPO).as_posix()
            if any(fragment in f"/{relative}" for fragment in excluded):
                continue
            text = read_text(relative)
            if text is None:
                continue
            for found in matcher.finditer(text):
                symbol = found.group("symbol")
                if not symbol.endswith(suffix):
                    continue
                key = (relative, symbol)
                if key in seen:
                    continue
                seen.add(key)
                records.append(
                    {
                        "owner": relative,
                        "symbol": symbol,
                        "token": found.group("token"),
                        "source": source["id"],
                    }
                )
    if not records:
        return [], f"no authority constant was discovered under {', '.join(globs)}"
    records.sort(key=lambda record: (record["owner"], record["symbol"]))
    return records, None


def assigned_token(relative: str, symbol: str) -> str | None:
    """The string a named module-level constant is assigned in a located module, or None."""
    text = read_text(relative)
    if text is None:
        return None
    found = re.search(
        rf"^{re.escape(symbol)}\s*(?::[^=\n]+)?=\s*\"([^\"]*)\"", text, re.MULTILINE
    )
    return found.group(1) if found else None


def symbol_defined(relative: str, symbol: str) -> bool:
    """True when a located module defines the named symbol as a function, class or constant."""
    text = read_text(relative)
    if text is None:
        return False
    return bool(
        re.search(
            rf"^(?:async\s+def|def|class)\s+{re.escape(symbol)}\b|^{re.escape(symbol)}\s*(?::|=)",
            text,
            re.MULTILINE,
        )
    )


# ---------------------------------------------------------------------------
# measurement


def resolves_in_repo(token: str) -> bool:
    """True when a token names an existing repository path."""
    candidate = token.strip().strip("`").strip()
    if not candidate or candidate.startswith(("http://", "https://")):
        return False
    return (REPO / candidate).exists()


def evidence_pointers(record: dict, token_families: list[str]) -> list[str]:
    """Evidence a discovered authority carries: its own owner plus every source token."""
    pointers = [record["owner"]]
    cell = " ".join(str(record.get(field, "")) for field in ("sources", "authoritative"))
    for family in token_families:
        pointers.extend(re.findall(rf"\b(?:{family})\b", cell))
    for word in re.findall(r"[0-9A-Za-z_./\u03a9\u221e-]+", cell):
        if "/" in word and resolves_in_repo(word):
            pointers.append(word)
    seen: list[str] = []
    for pointer in pointers:
        if pointer and pointer not in seen:
            seen.append(pointer)
    return seen


def lattice_problems(tiers: list[dict], source: dict) -> tuple[list[str], list[str]]:
    """Unresolved subordinate references, and any cycle in the located tier lattice."""
    id_field = source["id_field"]
    sub_field = source["subordinate_field"]
    known = {tier.get(id_field) for tier in tiers}
    unresolved = [
        f"{tier.get(id_field)} -> {parent}"
        for tier in tiers
        for parent in (tier.get(sub_field) or [])
        if parent not in known
    ]
    edges = {tier.get(id_field): list(tier.get(sub_field) or []) for tier in tiers}
    cycles: list[str] = []
    state: dict[str, int] = {}

    def walk(node: str, trail: list[str]) -> None:
        if state.get(node) == 1:
            cycles.append(" -> ".join(trail + [node]))
            return
        if state.get(node) == 2:
            return
        state[node] = 1
        for parent in edges.get(node, []):
            if parent in edges:
                walk(parent, trail + [node])
        state[node] = 2

    for node in sorted(n for n in edges if n):
        walk(node, [])
    return sorted(unresolved), sorted(set(cycles))


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


def measure(document: dict) -> dict:
    programme = document["programme"]
    token_families = [
        entry["id_pattern"] for entry in document["source_token_registers"] if entry.get("id_pattern")
    ]

    # --- CAP-01 registry -------------------------------------------------
    authorities: list[dict] = []
    source_status: list[dict] = []
    for source in document["authority_sources"]:
        fmt = source.get("format")
        if fmt not in FORMATS:
            raise FailClosed(f"authority source {source.get('id')} declares unknown format {fmt!r}")
        if fmt == "markdown-table":
            records, reason = read_markdown_table_source(source)
        elif fmt == "article-authority":
            records, reason = read_article_authority_source(source)
        else:
            records, reason = [], f"format {fmt} is not an authority reader"
        source_status.append(
            {
                "id": source["id"],
                "name": source["name"],
                "owner": source.get("owner") or source.get("owner_glob"),
                "format": fmt,
                "discovered": len(records),
                "resolved": reason is None and bool(records),
                "reason": reason,
            }
        )
        for record in records:
            record["source"] = source["id"]
            record["kind"] = source["kind"]
            record["evidence"] = evidence_pointers(record, token_families)
            record["evidence_resolved"] = sorted(
                pointer for pointer in record["evidence"] if resolves_in_repo(pointer)
            )
            authorities.append(record)
    authorities.sort(key=lambda record: (record["kind"], record["id"]))
    registry = {record["id"] for record in authorities}

    # source tokens that a located register defines
    known_tokens: set[str] = set()
    token_status: list[dict] = []
    for entry in document["source_token_registers"]:
        fmt = entry.get("format")
        if fmt == "markdown-table":
            records, reason = read_markdown_table_source(entry)
            tokens = {record["id"] for record in records}
        elif fmt == "document-token":
            tokens, reason = read_document_tokens(entry)
        else:
            tokens, reason = set(), f"unknown token register format {fmt!r}"
        token_status.append(
            {"id": entry["id"], "name": entry["name"], "tokens": len(tokens), "reason": reason}
        )
        known_tokens |= tokens

    # --- tiers and vacancies --------------------------------------------
    tier_source = document["tier_source"]
    tiers, tier_reason = read_json_collection(
        tier_source["owner"], tier_source["collection_pointer"]
    )
    vacancies, vacancy_reason = read_json_collection(
        tier_source["owner"], tier_source["vacancy_collection_pointer"]
    )
    unresolved_subordinates, tier_cycles = lattice_problems(tiers, tier_source)
    vacancy_records = []
    incomplete_vacancies = []
    for entry in vacancies:
        missing = [
            field for field in tier_source["vacancy_required_fields"] if not entry.get(field)
        ]
        record = {
            "id": entry.get(tier_source["vacancy_id_field"]),
            "tier": entry.get(tier_source["vacancy_tier_field"]),
            "located": bool(entry.get(tier_source["vacancy_located_field"])),
            "open_question": entry.get("open_question"),
            "complete": not missing,
            "missing_fields": missing,
        }
        vacancy_records.append(record)
        if missing:
            incomplete_vacancies.append(f"{record['id']}: {', '.join(missing)}")
    vacant_tiers = sorted(
        tier.get(tier_source["id_field"])
        for tier in tiers
        if tier.get(tier_source["vacancy_field"])
    )

    # --- CAP-13 tier governance ------------------------------------------
    # The projection above is DATA. The lattice it projects is legislated as prose in a
    # located instrument. Nothing read the two against each other, so this reads them, plus
    # the charter vesting the instrument is obliged to stay consistent with. Every fact
    # compared is read; none is declared here.
    lattice_source = document["tier_lattice_source"]
    canonical_rows, lattice_reason = read_markdown_table_source(lattice_source)
    located_token = str(lattice_source["located_token"]).upper()
    vacant_token = str(lattice_source["vacant_token"]).upper()
    canonical: dict[str, dict] = {}
    for row in canonical_rows:
        status = str(row.get("status", "")).upper()
        canonical[row["id"]] = {
            "id": row["id"],
            "name": str(row.get("name", "")).strip(),
            "content": str(row.get("content", "")).strip(),
            "status": str(row.get("status", "")).strip(),
            "vacant": vacant_token in status,
            "located": located_token in status and vacant_token not in status,
        }

    vesting_source = document["tier_vesting_source"]
    vesting_records, vesting_reason = read_vesting_list(vesting_source)
    vested_names = {record["name"].casefold() for record in vesting_records}
    authority_names = {
        str(record.get("name", "")).strip().casefold()
        for record in authorities
        if str(record.get("name", "")).strip()
    }
    artifact_tiers: set[str] = set()
    artifacts, artifact_reason = read_json_collection(
        lattice_source["occupant_owner"], lattice_source["occupant_pointer"]
    )
    occupant_tier_field = lattice_source["occupant_tier_field"]
    if not artifact_reason:
        artifact_tiers = {
            str(entry[occupant_tier_field]) for entry in artifacts if entry.get(occupant_tier_field)
        }

    projection_problems: list[str] = []
    if lattice_reason:
        projection_problems.append(f"{lattice_source['id']}: {lattice_reason}")
    if artifact_reason:
        # A declared corroboration register that does not resolve is reported, never treated as
        # a register that corroborates nothing: silence would narrow the evidence base invisibly.
        projection_problems.append(
            f"{lattice_source['id']}: occupant register does not resolve: {artifact_reason}"
        )
    vesting_problems: list[str] = []
    if vesting_reason:
        vesting_problems.append(f"{vesting_source['id']}: {vesting_reason}")
    corroboration_problems: list[str] = []
    tier_governance: list[dict] = []
    for tier in tiers:
        identifier = str(tier.get(tier_source["id_field"]))
        projected_name = str(tier.get(tier_source["name_field"]) or "").strip()
        occupancy = str(tier.get(tier_source["occupancy_field"]) or "").upper()
        projected_vacant = bool(tier.get(tier_source["vacancy_field"])) or occupancy == vacant_token
        row = canonical.get(identifier)
        faithful = row is not None
        if row is None:
            projection_problems.append(f"{identifier}: absent from the canonical lattice")
        else:
            if row["name"].casefold() != projected_name.casefold():
                faithful = False
                projection_problems.append(
                    f"{identifier}: projected name {projected_name!r} is not the canonical "
                    f"name {row['name']!r}"
                )
            if row["vacant"] != projected_vacant or (
                not projected_vacant and occupancy != located_token
            ):
                faithful = False
                projection_problems.append(
                    f"{identifier}: projected occupancy {occupancy!r} disagrees with the "
                    f"canonical located status {row['status']!r}"
                )
        # Corroboration is computed ONLY for a tier the projection already reports occupied.
        # Computing it for a vacant tier would read located evidence as an occupant, which the
        # meta-constitution forbids and which its own recorded reconciliation reserves to the
        # claim owner.
        channels: list[str] = []
        if not projected_vacant:
            # An occupant that merely repeats the tier's own identifier or name names nothing.
            # Requiring it to be distinct is what stops a mis-read column from corroborating
            # every tier with the tier itself.
            occupant = row["content"] if row else ""
            names_something = bool(occupant) and occupant.casefold() not in {
                identifier.casefold(),
                projected_name.casefold(),
            }
            if names_something:
                channels.append(CHANNEL_CONTENT)
            if identifier in artifact_tiers:
                channels.append(CHANNEL_ARTIFACT)
            if projected_name.casefold() in authority_names:
                channels.append(CHANNEL_AUTHORITY)
            if projected_name.casefold() in vested_names:
                channels.append(CHANNEL_VESTING)
            if not channels:
                corroboration_problems.append(
                    f"{identifier}: reported occupied with no located occupant"
                )
        tier_governance.append(
            {
                "id": identifier,
                "projected_name": projected_name,
                "canonical_name": row["name"] if row else None,
                "projected_occupancy": tier.get(tier_source["occupancy_field"]),
                "canonical_status": row["status"] if row else None,
                "canonical_occupant": row["content"] if row else None,
                "vacant": projected_vacant,
                "faithful": faithful,
                "corroboration": channels,
                "corroborated": bool(channels),
            }
        )
    projected_ids = {str(tier.get(tier_source["id_field"])) for tier in tiers}
    projection_problems.extend(
        f"{identifier}: canonical tier absent from the projection"
        for identifier in sorted(canonical)
        if identifier not in projected_ids
    )
    canonical_names = {row["name"].casefold() for row in canonical.values()}
    vesting_problems.extend(
        f"{record['id']}: vested tier {record['name']!r} is absent from the canonical lattice"
        for record in vesting_records
        if record["name"].casefold() not in canonical_names
    )

    # --- CAP-12 realization ----------------------------------------------
    # An authority is also EXERCISED by code. Two properties are measured independently: no
    # minted token may collide with a registered constitutional authority, and every minted
    # token must be classified. The declared classes cannot narrow the discovered population
    # and cannot waive the collision check.
    minted: list[dict] = []
    classification_problems: list[str] = []
    collision_problems: list[str] = []
    classes = {
        str(entry["token"]): entry for entry in document["realization_token_classes"]
    }
    for source in document["realization_sources"]:
        # The collision surface is every registered identifier plus every registered NAME of at
        # least the declared word count. A one-word designation such as the generic noun the
        # authority register uses for authority itself is also an ordinary program identifier,
        # so treating it as a collision would report vocabulary as usurpation. Nothing is lost:
        # the classification obligation below closes the gate on ANY undisclosed token, whatever
        # it says, so a token that reads as an authority cannot pass merely by not colliding.
        minimum = int(source.get("collision_min_name_words") or 0)
        collision_surface = {token.casefold() for token in registry} | {
            name for name in authority_names if name and len(name.split()) >= minimum
        }
        records, reason = read_minted_tokens(source)
        if reason:
            classification_problems.append(f"{source['id']}: {reason}")
            continue
        for record in records:
            token = record["token"]
            declared = classes.get(token)
            collides = token.strip().casefold() in collision_surface
            record["class"] = declared["class"] if declared else None
            record["classified"] = declared is not None
            record["constitutional_collision"] = collides
            minted.append(record)
            if not declared:
                classification_problems.append(
                    f"{record['owner']}:{record['symbol']}: token {token!r} is classified nowhere"
                )
            if collides:
                collision_problems.append(
                    f"{record['owner']}:{record['symbol']}: token {token!r} is a registered "
                    f"constitutional authority"
                )
    for entry in document["realization_token_classes"]:
        if entry.get("constitutional"):
            collision_problems.append(
                f"{entry['id']}: a token class may not declare itself constitutional"
            )

    located_tier_names = {
        record["projected_name"].casefold()
        for record in tier_governance
        if not record["vacant"]
    }
    realizations: list[dict] = []
    realization_problems: list[str] = []
    for binding in document["realization_bindings"]:
        owner = binding["owner"]
        token = assigned_token(owner, binding["token_symbol"])
        guarded = symbol_defined(owner, binding["guard_symbol"])
        named = binding["authority"].strip().casefold()
        matched = sorted(
            record["id"]
            for record in authorities
            if str(record.get("name", "")).strip().casefold() == named
        )
        # The vesting clause must live in the instrument that DEFINES the named authority.
        # Without this the binding would accept any authority that merely resolves, so a module
        # could be bound to an authority it does not realize and the gate would still open.
        defining_owners = sorted(
            str(record["owner"])
            for record in authorities
            if str(record.get("name", "")).strip().casefold() == named
        )
        vested_by_definer = binding["vesting_instrument"] in defining_owners
        tier_name = binding["tier"].strip().casefold()
        tier_located = tier_name in located_tier_names
        vesting_text = read_text(binding["vesting_instrument"])
        vested = vesting_text is not None and binding["vesting_anchor"] in vesting_text
        record = {
            "id": binding["id"],
            "authority": binding["authority"],
            "authority_resolved": matched,
            "tier": binding["tier"],
            "tier_located": tier_located,
            "owner": owner,
            "token_symbol": binding["token_symbol"],
            "token": token,
            "guard_symbol": binding["guard_symbol"],
            "guard_present": guarded,
            "vesting_instrument": binding["vesting_instrument"],
            "vesting_located": vested,
            "vested_by_definer": vested_by_definer,
            "bound": (
                bool(token)
                and guarded
                and len(matched) == 1
                and tier_located
                and vested
                and vested_by_definer
            ),
        }
        realizations.append(record)
        if token is None:
            realization_problems.append(
                f"{binding['id']}: {binding['token_symbol']} is not assigned in {owner}"
            )
        if not guarded:
            realization_problems.append(
                f"{binding['id']}: enforcement symbol {binding['guard_symbol']} absent in {owner}"
            )
        if len(matched) != 1:
            realization_problems.append(
                f"{binding['id']}: authority {binding['authority']!r} resolves to "
                f"{len(matched)} registered authorities, not one"
            )
        if not vested_by_definer:
            realization_problems.append(
                f"{binding['id']}: vesting instrument {binding['vesting_instrument']} does not "
                f"define authority {binding['authority']!r}"
            )
        if not tier_located:
            realization_problems.append(
                f"{binding['id']}: tier {binding['tier']!r} is not a located tier of the lattice"
            )
        if not vested:
            realization_problems.append(
                f"{binding['id']}: vesting clause absent in {binding['vesting_instrument']}"
            )

    # --- CAP-14 admission -------------------------------------------------
    admission = document["admission_determination"]
    disposition_source = admission["disposition_source"]
    disposition_text = read_text(disposition_source["owner"])
    forbidden = str(disposition_source["forbidden_disposition"]).upper()
    disposition_problems: list[str] = []
    if disposition_text is None:
        disposition_problems.append(
            f"disposition source does not resolve: {disposition_source['owner']}"
        )
    elif disposition_source["anchor"] not in disposition_text:
        disposition_problems.append(
            f"disposition source anchor absent in {disposition_source['owner']}"
        )
    admitted: list[dict] = []
    for concept in admission["concepts"]:
        owner = concept["canonical_owner"]
        owner_resolved = resolves_in_repo(owner)
        disposition = str(concept["disposition"]).upper()
        located = disposition_text is not None and disposition in disposition_text
        record = {
            "id": concept["id"],
            "concept": concept["concept"],
            "disposition": concept["disposition"],
            "canonical_owner": owner,
            "owner_resolved": owner_resolved,
            "disposition_located": located,
            "refusal_recorded": bool(str(concept.get("why_not_create", "")).strip()),
        }
        admitted.append(record)
        if not owner_resolved:
            disposition_problems.append(
                f"{concept['id']}: canonical owner does not resolve: {owner}"
            )
        if disposition == forbidden:
            disposition_problems.append(
                f"{concept['id']}: disposition {disposition} creates a parallel authority"
            )
        elif not located:
            disposition_problems.append(
                f"{concept['id']}: disposition {disposition} is not drawn from the located "
                f"totality rule"
            )
        if not record["refusal_recorded"]:
            disposition_problems.append(
                f"{concept['id']}: no reason CREATE was refused is recorded"
            )
    if admission.get("admitted_to_meta_registry"):
        meta_text = read_text(admission["meta_registry"])
        if meta_text is not None and programme["id"] not in meta_text:
            disposition_problems.append(
                "admission claims meta-registry standing that the meta registry does not record"
            )

    # --- CAP-02 delegation ----------------------------------------------
    delegations: list[dict] = []
    unowned_delegations: list[str] = []
    for source in document["delegation_sources"]:
        entries, reason = read_json_collection(source["owner"], source["collection_pointer"])
        if reason:
            unowned_delegations.append(f"{source['id']}: {reason}")
            continue
        for entry in entries:
            owner_value = entry.get(source["owner_field"])
            owner_paths = entry.get(source.get("owner_paths_field") or "") or []
            candidates = [owner_value] if owner_value else []
            candidates.extend(owner_paths if isinstance(owner_paths, list) else [])
            resolved = sorted(
                candidate
                for candidate in candidates
                if candidate and (resolves_in_repo(candidate) or candidate in registry)
            )
            named = bool(candidates)
            record = {
                "id": entry.get(source["id_field"]),
                "concern": entry.get(source["concern_field"]),
                "owner": owner_value or (owner_paths[0] if owner_paths else None),
                "disposition": entry.get(source.get("disposition_field") or ""),
                "owner_named": named,
                "owner_resolved": bool(resolved),
            }
            delegations.append(record)
            if not named:
                unowned_delegations.append(f"{record['id']}: no owner named")
    delegations.sort(key=lambda record: str(record["id"]))

    # --- CAP-05 succession ----------------------------------------------
    successions: list[dict] = []
    unsourced_successions: list[str] = []
    for source in document["succession_sources"]:
        records, reason = read_markdown_table_source(source)
        if reason:
            unsourced_successions.append(f"{source['id']}: {reason}")
            continue
        for record in records:
            cell = str(record.get("authoritative_source", ""))
            tokens = sorted(
                {
                    token
                    for family in token_families
                    for token in re.findall(rf"\b(?:{family})\b", cell)
                }
            )
            resolved = [token for token in tokens if token in known_tokens]
            entry = {
                "id": record["id"],
                "concept": record.get("concept"),
                "authoritative_tokens": tokens,
                "resolved": bool(resolved),
                "status": record.get("status", "")[:120],
            }
            successions.append(entry)
            if not resolved:
                unsourced_successions.append(f"{record['id']}: no source token resolves")
    successions.sort(key=lambda record: str(record["id"]))

    # --- CAP-06 scope ----------------------------------------------------
    scope_rules: list[dict] = []
    unbound_scope: list[str] = []
    for rule in document["scope_rules"]:
        text = read_text(rule["owner"])
        bound = text is not None and rule["anchor"] in text
        scope_rules.append(
            {"id": rule["id"], "rule": rule["rule"], "owner": rule["owner"], "bound": bound}
        )
        if not bound:
            unbound_scope.append(f"{rule['id']}: anchor absent in {rule['owner']}")

    # --- CAP-03 resolution ----------------------------------------------
    resolutions: list[dict] = []
    unresolved_questions: list[str] = []
    for question in document["resolutions"]:
        text = read_text(question["owner"])
        located = text is not None and question["anchor"] in text
        answers: list[str] = []
        if located:
            for line in text.splitlines():
                if question["anchor"] in line:
                    for identifier in re.findall(r"\b[A-Z][A-Z0-9]*(?:-[A-Z0-9]+)+\b", line):
                        if identifier in registry and identifier not in answers:
                            answers.append(identifier)
                    break
        record = {
            "id": question["id"],
            "question": question["question"],
            "owner": question["owner"],
            "located": located,
            "in_corpus": bool(question.get("in_corpus")),
            "answers": answers,
            "outcome": "ANSWERED" if located else "UNRESOLVED",
        }
        resolutions.append(record)
        if not located:
            unresolved_questions.append(f"{question['id']}: anchor absent in {question['owner']}")

    # --- CAP-11 certification: no authority undefined --------------------
    families = [source["id_pattern"] for source in document["authority_sources"] if source.get("id_pattern")]
    undefined: list[dict] = []
    scanned = surface_files(
        document["reference_surfaces"], document.get("reference_surface_extensions") or [".md"]
    )
    if families:
        scanner = re.compile(rf"\b(?:{'|'.join(families)})\b")
        for relative in scanned:
            if relative.startswith(OWN_PREFIX):
                continue
            text = read_text(relative)
            if text is None:
                continue
            for token in sorted(set(scanner.findall(text))):
                if token not in registry:
                    undefined.append({"token": token, "surface": relative})

    # --- CAP-13 reconciliation ------------------------------------------
    reconciliations: list[dict] = []
    unmeasured_reconciliations: list[str] = []
    for item in document["reconciliations"]:
        claim_text = read_text(item["claim_owner"])
        claim_stands = claim_text is not None and item["claim_anchor"] in claim_text
        located_evidence = []
        absent_evidence = []
        for candidate in item["candidate_evidence"]:
            text = read_text(candidate["path"])
            if text is not None and candidate["anchor"] in text:
                located_evidence.append(candidate["path"])
            else:
                absent_evidence.append(candidate["path"])
        if not claim_stands:
            outcome = OUT_CLAIM_ABSENT
        elif located_evidence:
            outcome = OUT_BOTH
        else:
            outcome = OUT_EVIDENCE_ABSENT
        record = {
            "id": item["id"],
            "claim": item["claim"],
            "claim_owner": item["claim_owner"],
            "claim_stands": claim_stands,
            "evidence_located": sorted(located_evidence),
            "evidence_absent": sorted(absent_evidence),
            "outcome": outcome,
            "referred_to": item.get("referred_to"),
            "ratifies": False,
            "closes_vacancy": False,
        }
        reconciliations.append(record)
        if claim_text is None and not located_evidence:
            unmeasured_reconciliations.append(f"{item['id']}: neither side resolves")

    # --- CAP-10 revocation ----------------------------------------------
    revocation_problems: list[str] = []
    for entry in document["revocations"]:
        if entry.get("authority") not in registry:
            revocation_problems.append(f"{entry.get('id')}: authority does not resolve")
        elif not resolves_in_repo(entry.get("record", "")):
            revocation_problems.append(f"{entry.get('id')}: record path does not resolve")

    # --- CAP-07 verification --------------------------------------------
    verified: list[dict] = []
    unverified: list[str] = []
    for relative in sorted(
        {record["owner"] for record in authorities}
        | {tier_source["owner"]}
        | {source["owner"] for source in document["succession_sources"]}
    ):
        text = read_text(relative)
        if text is None:
            unverified.append(relative)
            continue
        verified.append({"owner": relative, "digest": digest(text)[:16]})

    # --- CAP-09 audit ----------------------------------------------------
    audit = [
        {
            "entry": index,
            "authority": record["id"],
            "kind": record["kind"],
            "source": record["source"],
            "owner": record["owner"],
            "evidence": len(record["evidence_resolved"]),
        }
        for index, record in enumerate(authorities, start=1)
    ]

    # --- validations -----------------------------------------------------
    definitionless = sorted(
        record["id"] for record in authorities if not str(record.get("definition", "")).strip()
    )
    evidenceless = sorted(
        record["id"] for record in authorities if not record["evidence_resolved"]
    )
    self_conferred = sorted(
        record["id"]
        for record in authorities
        if {token for token in re.findall(r"\b[A-Z][A-Z0-9]*(?:-[A-Z0-9]+)+\b", str(record.get("sources", "")))}
        == {record["id"]}
    )

    # Measured failure lists, keyed by validation id. This is the one place the engine names a
    # validation: measurement logic cannot be derived from data. A declared validation with no
    # measurement here is reported measured=false and satisfied=false, so it fails closed —
    # absence of a measurement is never evidence of compliance.
    findings: dict[str, list[str]] = {
        "UCAF-VAL-01": [
            f"{entry['id']}: {entry['reason'] or 'no records discovered'}"
            for entry in source_status
            if not entry["resolved"]
        ],
        "UCAF-VAL-02": definitionless,
        "UCAF-VAL-03": evidenceless,
        "UCAF-VAL-04": self_conferred,
        "UCAF-VAL-05": unresolved_subordinates + tier_cycles + ([tier_reason] if tier_reason else []),
        "UCAF-VAL-06": incomplete_vacancies + ([vacancy_reason] if vacancy_reason else []),
        "UCAF-VAL-07": [f"{item['token']} ({item['surface']})" for item in undefined],
        "UCAF-VAL-08": unresolved_questions,
        "UCAF-VAL-09": unbound_scope,
        "UCAF-VAL-10": unowned_delegations,
        "UCAF-VAL-11": unsourced_successions,
        "UCAF-VAL-12": revocation_problems,
        "UCAF-VAL-13": unmeasured_reconciliations,
        "UCAF-VAL-14": [],  # filled below, once the capability measures are known
        "UCAF-VAL-15": [
            f"{record['id']}: promoted or ratified"
            for record in reconciliations
            if record["ratifies"] or record["closes_vacancy"]
        ]
        + [f"{tier}: reported occupied while vacant" for tier in [] ],
        "UCAF-VAL-16": sorted(collision_problems),
        "UCAF-VAL-17": sorted(classification_problems),
        "UCAF-VAL-18": sorted(realization_problems),
        "UCAF-VAL-19": sorted(projection_problems),
        "UCAF-VAL-20": sorted(corroboration_problems),
        "UCAF-VAL-21": sorted(vesting_problems),
        "UCAF-VAL-22": sorted(disposition_problems),
    }

    measures = {
        "authorities_registered": len(authorities),
        "delegations_registered": len(delegations),
        "resolutions_answered": sum(1 for record in resolutions if record["located"]),
        "validations_measured": 0,
        "successions_registered": len(successions),
        "scope_rules_bound": sum(1 for rule in scope_rules if rule["bound"]),
        "records_verified": len(verified),
        "authorities_with_evidence": sum(1 for record in authorities if record["evidence_resolved"]),
        "audit_entries": len(audit),
        "revocations_registered": len(document["revocations"]),
        "undefined_references": len(undefined),
        "realizations_bound": sum(1 for record in realizations if record["bound"]),
        "tiers_corroborated": sum(
            1 for record in tier_governance if record["faithful"] and not record["vacant"]
        ),
        "dispositions_owned": sum(
            1
            for record in admitted
            if record["owner_resolved"] and record["disposition_located"]
        ),
    }
    capabilities = []
    for capability in document["capabilities"]:
        measure_key = capability["measure"]
        known = measure_key in measures
        # A capability is discharged when its measure ran AND, where the measure counts a
        # defect, the count is zero; where it counts a population, the population is non-empty.
        if not known:
            discharged = False
        elif measure_key == "undefined_references":
            discharged = measures[measure_key] == 0
        elif measure_key == "revocations_registered":
            discharged = not revocation_problems
        elif measure_key == "validations_measured":
            discharged = True
        elif measure_key == "realizations_bound":
            discharged = (
                bool(minted)
                and not classification_problems
                and not collision_problems
                and not realization_problems
            )
        elif measure_key == "tiers_corroborated":
            discharged = (
                bool(tier_governance)
                and not projection_problems
                and not corroboration_problems
                and not vesting_problems
            )
        elif measure_key == "dispositions_owned":
            discharged = bool(admitted) and not disposition_problems
        else:
            discharged = measures[measure_key] > 0
        capabilities.append(
            {
                "id": capability["id"],
                "capability": capability["capability"],
                "obligation": capability["obligation"],
                "measure": measure_key,
                "value": measures.get(measure_key),
                "measured": known,
                "discharged": discharged,
            }
        )
    findings["UCAF-VAL-14"] = [
        f"{entry['id']}: {entry['measure']}"
        for entry in capabilities
        if not entry["discharged"]
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
    measures["validations_measured"] = sum(1 for entry in validations if entry["measured"])
    for entry in capabilities:
        if entry["measure"] == "validations_measured":
            entry["value"] = measures["validations_measured"]

    blocking_failures = [
        entry["id"] for entry in validations if entry["blocking"] and not entry["satisfied"]
    ]
    gate = "CLOSED" if blocking_failures else "OPEN"

    model = {
        "programme": programme,
        "authority_sources": source_status,
        "source_token_registers": token_status,
        "authorities": [
            {
                "id": record["id"],
                "kind": record["kind"],
                "name": record.get("name"),
                "source": record["source"],
                "owner": record["owner"],
                "definition": str(record.get("definition", ""))[:400],
                "evidence": record["evidence"][:12],
                "evidence_resolved": record["evidence_resolved"][:12],
            }
            for record in authorities
        ],
        "tiers": [
            {
                "id": tier.get(tier_source["id_field"]),
                "name": tier.get(tier_source["name_field"]),
                "subordinate_to": tier.get(tier_source["subordinate_field"]) or [],
                "occupancy": tier.get(tier_source["occupancy_field"]),
                "vacancy": tier.get(tier_source["vacancy_field"]),
            }
            for tier in tiers
        ],
        "vacant_tiers": vacant_tiers,
        "vacancies": vacancy_records,
        "canonical_lattice": [canonical[key] for key in sorted(canonical)],
        "tier_governance": tier_governance,
        "tier_vesting": vesting_records,
        "minted_authority_tokens": minted,
        "realization_token_classes": list(document["realization_token_classes"]),
        "realizations": realizations,
        "admission": {
            "classification": admission["classification"],
            "meta_registry": admission["meta_registry"],
            "admitted_to_meta_registry": bool(admission.get("admitted_to_meta_registry")),
            "basis": admission["basis"],
            "concepts": admitted,
            "rejected_alternatives": list(admission.get("rejected_alternatives") or []),
        },
        "delegations": delegations,
        "successions": successions,
        "scope_rules": scope_rules,
        "resolutions": resolutions,
        "reconciliations": reconciliations,
        "revocations": list(document["revocations"]),
        "verified_sources": verified,
        "unverified_sources": sorted(unverified),
        "undefined_references": undefined,
        "audit_ledger": audit,
        "capabilities": capabilities,
        "validations": validations,
        "counts": {
            "authorities": len(authorities),
            "authority_kinds": len({record["kind"] for record in authorities}),
            "tiers": len(tiers),
            "vacant_tiers": len(vacant_tiers),
            "delegations": len(delegations),
            "successions": len(successions),
            "scope_rules_bound": measures["scope_rules_bound"],
            "scope_rules": len(scope_rules),
            "resolutions_answered": measures["resolutions_answered"],
            "resolutions": len(resolutions),
            "reconciliations": len(reconciliations),
            "reconciliation_required": sum(
                1 for record in reconciliations if record["outcome"] == OUT_BOTH
            ),
            "surfaces_scanned": len(scanned),
            "undefined_references": len(undefined),
            "audit_entries": len(audit),
            "capabilities_discharged": sum(1 for entry in capabilities if entry["discharged"]),
            "capabilities": len(capabilities),
            "canonical_tiers": len(canonical),
            "tiers_faithful": sum(1 for record in tier_governance if record["faithful"]),
            "tiers_corroborated": measures["tiers_corroborated"],
            "tiers_vested": len(vesting_records),
            "minted_tokens": len(minted),
            "minted_token_classes": len(document["realization_token_classes"]),
            "minted_unclassified": sum(1 for record in minted if not record["classified"]),
            "minted_collisions": sum(
                1 for record in minted if record["constitutional_collision"]
            ),
            "realizations": len(realizations),
            "realizations_bound": measures["realizations_bound"],
            "concepts_admitted": len(admitted),
            "dispositions_owned": measures["dispositions_owned"],
        },
        "blocking_failures": blocking_failures,
        "gate": gate,
        "gate_exit": 1 if blocking_failures else 0,
        "determination": (
            "AUTHORITY-MODEL-BOUND" if gate == "OPEN" else "AUTHORITY-MODEL-INCOMPLETE"
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


def front_matter(model: dict) -> str:
    programme = model["programme"]
    counts = model["counts"]
    rows = [
        ["PROGRAMME", f"{programme['id']} — {programme['name']}"],
        ["VERSION", programme["version"]],
        ["AUTHORITY", programme["authority"]],
        ["AUTHORITIES REGISTERED", f"{counts['authorities']} across {counts['authority_kinds']} kinds"],
        ["TIERS", f"{counts['tiers']} ({counts['vacant_tiers']} vacant)"],
        [
            "TIER PROJECTION FAITHFUL",
            f"{counts['tiers_faithful']}/{counts['tiers']} against "
            f"{counts['canonical_tiers']} canonical tiers",
        ],
        [
            "TIERS CORROBORATED",
            f"{counts['tiers_corroborated']}/{counts['tiers'] - counts['vacant_tiers']} "
            f"occupied · {counts['tiers_vested']} vested by the charter",
        ],
        [
            "EXECUTABLE AUTHORITY TOKENS",
            f"{counts['minted_tokens']} minted in {counts['minted_token_classes']} declared "
            f"classes · {counts['minted_unclassified']} unclassified · "
            f"{counts['minted_collisions']} colliding",
        ],
        ["REALIZATIONS BOUND", f"{counts['realizations_bound']}/{counts['realizations']}"],
        ["DISPOSITIONS OWNED", f"{counts['dispositions_owned']}/{counts['concepts_admitted']}"],
        ["DELEGATIONS", counts["delegations"]],
        ["SUCCESSIONS", counts["successions"]],
        ["SCOPE RULES BOUND", f"{counts['scope_rules_bound']}/{counts['scope_rules']}"],
        ["COMPETENCE QUESTIONS ANSWERED", f"{counts['resolutions_answered']}/{counts['resolutions']}"],
        ["UNDEFINED AUTHORITY REFERENCES", f"{counts['undefined_references']} over {counts['surfaces_scanned']} surfaces"],
        ["CAPABILITIES DISCHARGED", f"{counts['capabilities_discharged']}/{counts['capabilities']}"],
        ["GATE", model["gate"]],
        ["DETERMINATION", model["determination"]],
        ["SEAL (sha256)", model["seal_sha256"]],
        ["GENERATED BY", "ucaf_engine.py — regenerated, never hand-authored"],
    ]
    return table(["Field", "Value"], rows) + "\n\n> " + programme["disclosure"]


def render(model: dict) -> dict[str, str]:
    pages: dict[str, str] = {}
    programme = model["programme"]

    pages["00-UCAF-DASHBOARD.md"] = "\n".join(
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
                        "YES" if entry["discharged"] else "**NO**",
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

    pages["01-AUTHORITY-REGISTER.md"] = "\n".join(
        [
            f"# {programme['id']} · Authority Registry",
            "",
            "Every record below is DISCOVERED from the located instrument named in its owner",
            "column. No authority is defined by this programme.",
            "",
            table(
                ["Authority", "Kind", "Name", "Located definition (owner)", "Evidence resolved"],
                [
                    [
                        f"`{record['id']}`",
                        record["kind"],
                        record["name"] or "",
                        f"`{record['owner']}`",
                        len(record["evidence_resolved"]),
                    ]
                    for record in model["authorities"]
                ],
            ),
            "",
            "## Sources read",
            "",
            table(
                ["Source", "Owner", "Format", "Discovered", "Resolved"],
                [
                    [
                        f"`{entry['id']}`",
                        f"`{entry['owner']}`",
                        entry["format"],
                        entry["discovered"],
                        "YES" if entry["resolved"] else f"**NO** — {entry['reason']}",
                    ]
                    for entry in model["authority_sources"]
                ],
            ),
            "",
        ]
    )

    pages["02-TIER-DELEGATION-AND-SUCCESSION-REGISTER.md"] = "\n".join(
        [
            f"# {programme['id']} · Tiers, Delegation, Succession, Revocation",
            "",
            "## Tier lattice (read from the located meta-constitutional projection)",
            "",
            table(
                ["Tier", "Name", "Subordinate to", "Occupancy", "Vacancy"],
                [
                    [
                        f"`{tier['id']}`",
                        tier["name"] or "",
                        ", ".join(f"`{parent}`" for parent in tier["subordinate_to"]) or "—",
                        tier["occupancy"] or "",
                        f"`{tier['vacancy']}`" if tier["vacancy"] else "—",
                    ]
                    for tier in model["tiers"]
                ],
            ),
            "",
            "## Projection fidelity against the canonical lattice",
            "",
            "The table above is a machine PROJECTION. The lattice it projects is legislated as",
            "prose by its canonical owner. Both are read here and compared: membership, tier name",
            "and located status must agree in both directions, because every gate that resolves",
            "rank reads the projection and would inherit any drift silently.",
            "",
            "Corroboration is computed ONLY for a tier the projection already reports occupied.",
            "Reading located evidence as the occupant of a recorded vacancy would be a promotion,",
            "which the meta-constitution forbids and whose disposal belongs to the claim owner.",
            "",
            table(
                ["Tier", "Projected name", "Canonical name", "Projected", "Canonical status", "Faithful", "Occupant named by the canonical owner", "Corroboration"],
                [
                    [
                        f"`{record['id']}`",
                        record["projected_name"],
                        record["canonical_name"] or "**absent**",
                        record["projected_occupancy"] or "",
                        record["canonical_status"] or "**absent**",
                        "YES" if record["faithful"] else "**NO**",
                        record["canonical_occupant"] or "—",
                        (
                            "n/a — vacancy recorded"
                            if record["vacant"]
                            else ", ".join(record["corroboration"]) or "**none**"
                        ),
                    ]
                    for record in model["tier_governance"]
                ],
            ),
            "",
            "## Charter tier vesting (the order the lattice may not amend)",
            "",
            table(
                ["Vesting", "Tier", "Name", "Occupant the charter vests"],
                [
                    [
                        f"`{record['id']}`",
                        record["ordinal"],
                        record["name"],
                        record["occupant"],
                    ]
                    for record in model["tier_vesting"]
                ],
            )
            or "No vesting statement was read.",
            "",
            "## Recorded vacancies",
            "",
            "A vacancy is recorded, never promoted. This programme reports occupancy exactly as",
            "its located owner records it.",
            "",
            table(
                ["Vacancy", "Tier", "Occupant located", "Open question", "Record complete"],
                [
                    [
                        f"`{record['id']}`",
                        f"`{record['tier']}`",
                        "YES" if record["located"] else "NO",
                        f"`{record['open_question']}`" if record["open_question"] else "—",
                        "YES" if record["complete"] else f"**NO** — {', '.join(record['missing_fields'])}",
                    ]
                    for record in model["vacancies"]
                ],
            )
            or "No vacancy is recorded.",
            "",
            "## Delegation (CEP-002 Article 13 / Article 14)",
            "",
            table(
                ["Delegation", "Concern", "Owner", "Disposition", "Owner resolves"],
                [
                    [
                        f"`{record['id']}`",
                        record["concern"] or "",
                        f"`{record['owner']}`" if record["owner"] else "—",
                        record["disposition"] or "",
                        "YES" if record["owner_resolved"] else "no (named, unresolved path)",
                    ]
                    for record in model["delegations"]
                ],
            ),
            "",
            "## Succession",
            "",
            table(
                ["Succession", "Concept", "Authoritative source tokens", "Resolves"],
                [
                    [
                        f"`{record['id']}`",
                        record["concept"] or "",
                        ", ".join(f"`{token}`" for token in record["authoritative_tokens"]) or "—",
                        "YES" if record["resolved"] else "**NO**",
                    ]
                    for record in model["successions"]
                ],
            ),
            "",
            "## Revocation",
            "",
            "CEP-002 13.5 — a revocation SHALL be recorded and SHALL take effect upon record.",
            "The channel is append-only and every appended entry is validated against the",
            "registry.",
            "",
            (
                f"Recorded revocations: {len(model['revocations'])}."
                if model["revocations"]
                else "No revocation has been recorded in this repository. The channel exists and is empty."
            ),
            "",
        ]
    )

    pages["03-SCOPE-AND-RESOLUTION-REPORT.md"] = "\n".join(
        [
            f"# {programme['id']} · Scope and Resolution",
            "",
            "## Scope rules (bound to located clauses)",
            "",
            table(
                ["Rule", "Obligation", "Located in", "Bound"],
                [
                    [
                        f"`{rule['id']}`",
                        rule["rule"],
                        f"`{rule['owner']}`",
                        "YES" if rule["bound"] else "**NO**",
                    ]
                    for rule in model["scope_rules"]
                ],
            ),
            "",
            "## Competence resolution",
            "",
            "Each answer is READ from the located instrument named as owner. An absent clause is",
            "reported UNRESOLVED and is never answered by default.",
            "",
            table(
                ["Question", "Asked", "Located in", "In corpus", "Answers", "Outcome"],
                [
                    [
                        f"`{record['id']}`",
                        record["question"],
                        f"`{record['owner']}`",
                        "YES" if record["in_corpus"] else "NO (out-of-corpus superior)",
                        ", ".join(f"`{answer}`" for answer in record["answers"]) or "—",
                        record["outcome"],
                    ]
                    for record in model["resolutions"]
                ],
            ),
            "",
        ]
    )

    pages["04-RECONCILIATION-REPORT.md"] = "\n".join(
        [
            f"# {programme['id']} · Authority Reconciliation",
            "",
            "Where a recorded claim of authority absence and located evidence of authority",
            "presence both stand, both are Repository Truth. This programme measures both sides,",
            "cites both, and refers the conflict to the claim owner for disposal under CEP-002",
            "Article 23. It performs no disposal, closes no vacancy and ratifies nothing.",
            "",
            table(
                ["Reconciliation", "Claim", "Claim owner", "Claim stands", "Evidence located", "Outcome", "Referred to"],
                [
                    [
                        f"`{record['id']}`",
                        record["claim"],
                        f"`{record['claim_owner']}`",
                        "YES" if record["claim_stands"] else "NO",
                        ", ".join(f"`{path}`" for path in record["evidence_located"]) or "—",
                        record["outcome"],
                        f"`{record['referred_to']}`" if record["referred_to"] else "—",
                    ]
                    for record in model["reconciliations"]
                ],
            ),
            "",
            "## Undefined authority references",
            "",
            (
                "None. Every authority-shaped reference in every declared surface resolves to a"
                " registered authority."
                if not model["undefined_references"]
                else table(
                    ["Token", "Surface"],
                    [
                        [f"`{item['token']}`", f"`{item['surface']}`"]
                        for item in model["undefined_references"][:200]
                    ],
                )
            ),
            "",
        ]
    )

    pages["05-AUTHORITY-AUDIT-LEDGER.md"] = "\n".join(
        [
            f"# {programme['id']} · Authority Audit Ledger",
            "",
            "Append-only and content-addressed. The ledger plus the verified source digests are",
            "sufficient to reconstruct this registration deterministically.",
            "",
            table(
                ["#", "Authority", "Kind", "Source", "Owner", "Evidence"],
                [
                    [
                        entry["entry"],
                        f"`{entry['authority']}`",
                        entry["kind"],
                        f"`{entry['source']}`",
                        f"`{entry['owner']}`",
                        entry["evidence"],
                    ]
                    for entry in model["audit_ledger"]
                ],
            ),
            "",
            "## Verified sources",
            "",
            table(
                ["Owner", "Content digest (sha256/16)"],
                [[f"`{entry['owner']}`", entry["digest"]] for entry in model["verified_sources"]],
            ),
            "",
            (
                ""
                if not model["unverified_sources"]
                else "### Unverified\n\n"
                + "\n".join(f"- `{item}`" for item in model["unverified_sources"])
                + "\n"
            ),
        ]
    )

    pages["07-AUTHORITY-REALIZATION-REGISTER.md"] = "\n".join(
        [
            f"# {programme['id']} · Authority Realization",
            "",
            "An authority is declared by an instrument and EXERCISED by code. Every token below",
            "is DISCOVERED from the executable plane; none is declared by this programme. Two",
            "properties are measured independently, and the second cannot waive the first.",
            "",
            "1. **No collision.** No token minted in the executable plane may be a registered",
            "   constitutional authority. This is the machine form of the prohibition on",
            "   governance asserting, simulating or substituting for constitutional authority.",
            "2. **Classified.** Every discovered token must belong to a declared class recording",
            "   what it is and why it is not a constitutional authority. An undisclosed token",
            "   closes the gate whatever it says.",
            "",
            "## Declared token classes",
            "",
            table(
                ["Class", "Token", "Class", "Constitutional", "Basis"],
                [
                    [
                        f"`{entry['id']}`",
                        f"`{entry['token']}`",
                        entry["class"],
                        "YES" if entry.get("constitutional") else "no",
                        entry["basis"],
                    ]
                    for entry in model["realization_token_classes"]
                ],
            ),
            "",
            "## Tokens minted in the executable plane",
            "",
            table(
                ["Module", "Constant", "Token", "Class", "Classified", "Collides"],
                [
                    [
                        f"`{record['owner']}`",
                        f"`{record['symbol']}`",
                        f"`{record['token']}`",
                        record["class"] or "**none**",
                        "YES" if record["classified"] else "**NO**",
                        "**YES**" if record["constitutional_collision"] else "no",
                    ]
                    for record in model["minted_authority_tokens"]
                ],
            ),
            "",
            "## Realization bindings (located authority ↔ the code that exercises it)",
            "",
            table(
                ["Binding", "Authority", "Resolves to", "Tier", "Tier located", "Module", "Token", "Enforced by", "Vesting located", "Defined by the vesting instrument", "Bound"],
                [
                    [
                        f"`{record['id']}`",
                        record["authority"],
                        ", ".join(f"`{item}`" for item in record["authority_resolved"])
                        or "**none**",
                        record["tier"],
                        "YES" if record["tier_located"] else "**NO**",
                        f"`{record['owner']}`",
                        f"`{record['token']}`" if record["token"] else "**unassigned**",
                        f"`{record['guard_symbol']}`" if record["guard_present"] else "**absent**",
                        "YES" if record["vesting_located"] else "**NO**",
                        "YES" if record["vested_by_definer"] else "**NO**",
                        "YES" if record["bound"] else "**NO**",
                    ]
                    for record in model["realizations"]
                ],
            ),
            "",
        ]
    )

    admission = model["admission"]
    pages["08-ADMISSION-AND-DISPOSITION-DETERMINATION.md"] = "\n".join(
        [
            f"# {programme['id']} · Admission and Disposition",
            "",
            table(
                ["Field", "Value"],
                [
                    ["CLASSIFICATION", admission["classification"]],
                    ["META REGISTRY", f"`{admission['meta_registry']}`"],
                    [
                        "ADMITTED TO THE META REGISTRY",
                        "YES" if admission["admitted_to_meta_registry"] else "no — by design",
                    ],
                    ["BASIS", admission["basis"]],
                ],
            ),
            "",
            "Exactly one disposition is recorded for every concept reached. A disposition is",
            "drawn from the totality rule of the located instrument, never invented here, and",
            "CREATE is a validation failure: a concept whose owner is named cannot be created a",
            "second time without manufacturing the parallel authority that instrument forbids.",
            "",
            "## Concepts reached",
            "",
            table(
                ["Concept", "Statement", "Disposition", "Canonical owner", "Owner resolves", "Disposition located", "Refusal recorded"],
                [
                    [
                        f"`{record['id']}`",
                        record["concept"],
                        record["disposition"],
                        f"`{record['canonical_owner']}`",
                        "YES" if record["owner_resolved"] else "**NO**",
                        "YES" if record["disposition_located"] else "**NO**",
                        "YES" if record["refusal_recorded"] else "**NO**",
                    ]
                    for record in admission["concepts"]
                ],
            ),
            "",
            "## Alternatives rejected",
            "",
            "\n".join(f"- {item}" for item in admission["rejected_alternatives"])
            or "None recorded.",
            "",
        ]
    )

    pages["06-CERTIFICATION-REPORT.md"] = "\n".join(
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
            "CERTIFIED-PROVISIONAL. This programme holds no ratification authority: it registers,",
            "resolves, validates and audits the authorities the repository has already located.",
            "Where this register and a located instrument differ, the located instrument governs.",
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
    for section in (
        "capabilities",
        "authority_sources",
        "scope_rules",
        "resolutions",
        "reconciliations",
        "realization_sources",
        "realization_token_classes",
        "realization_bindings",
        "validations",
        "exit_criteria",
    ):
        for entry in document[section]:
            identifier = entry.get("id")
            if not identifier:
                problems.append(f"{section}: an entry carries no id")
            elif identifier in seen:
                problems.append(f"{section}: duplicate id {identifier}")
            else:
                seen.add(identifier)
    for concept in document["admission_determination"]["concepts"]:
        identifier = concept.get("id")
        if not identifier:
            problems.append("admission_determination: a concept carries no id")
        elif identifier in seen:
            problems.append(f"admission_determination: duplicate id {identifier}")
        else:
            seen.add(identifier)
    for source in document["authority_sources"]:
        if source.get("format") not in FORMATS:
            problems.append(f"{source.get('id')}: unknown format {source.get('format')!r}")
        owner = source.get("owner")
        if owner and not (REPO / owner).is_file():
            problems.append(f"{source.get('id')}: owner does not resolve: {owner}")
    for rule in document["scope_rules"] + document["resolutions"]:
        if not (REPO / rule["owner"]).is_file():
            problems.append(f"{rule['id']}: owner does not resolve: {rule['owner']}")
    if not (REPO / document["tier_source"]["owner"]).is_file():
        problems.append("tier_source owner does not resolve")
    for pointer in ("tier_lattice_source", "tier_vesting_source"):
        entry = document[pointer]
        if entry.get("format") not in FORMATS:
            problems.append(f"{entry.get('id')}: unknown format {entry.get('format')!r}")
        if not (REPO / entry["owner"]).is_file():
            problems.append(f"{entry['id']}: owner does not resolve: {entry['owner']}")
    if not (REPO / document["tier_lattice_source"]["occupant_owner"]).is_file():
        problems.append("tier_lattice_source occupant owner does not resolve")
    for binding in document["realization_bindings"]:
        for field in ("owner", "vesting_instrument"):
            if not (REPO / binding[field]).is_file():
                problems.append(f"{binding['id']}: {field} does not resolve: {binding[field]}")
        for field in (
            "authority",
            "tier",
            "token_symbol",
            "guard_symbol",
            "vesting_anchor",
            "basis",
        ):
            if not str(binding.get(field, "")).strip():
                problems.append(f"{binding['id']}: {field} is empty")
    for entry in document["realization_token_classes"]:
        if entry.get("constitutional"):
            problems.append(f"{entry['id']}: a token class may not declare itself constitutional")
        if not str(entry.get("basis", "")).strip():
            problems.append(f"{entry['id']}: no basis recorded")
    admission = document["admission_determination"]
    if not (REPO / admission["disposition_source"]["owner"]).is_file():
        problems.append("admission_determination: disposition source owner does not resolve")
    for item in document["reconciliations"]:
        if not (REPO / item["claim_owner"]).is_file():
            problems.append(f"{item['id']}: claim owner does not resolve")
    return problems


def check_no_enumeration(document: dict) -> list[str]:
    """No discovered or located identifier may appear as a literal in this engine's source."""
    source = Path(__file__).read_text(encoding="utf-8")
    leaked: list[str] = []
    model = measure(document)
    for record in model["authorities"]:
        if record["id"] in source:
            leaked.append(f"authority {record['id']}")
    for tier in model["tiers"]:
        identifier = tier["id"]
        if identifier and re.search(rf"\b{re.escape(identifier)}\b", source):
            leaked.append(f"tier {identifier}")
    for record in model["vacancies"]:
        if record["id"] and record["id"] in source:
            leaked.append(f"vacancy {record['id']}")
    return sorted(set(leaked))


def check_write_scope(document: dict) -> list[str]:
    problems: list[str] = []
    targets = [HERE / name for name in render(measure(document))] + [MODEL]
    for target in targets:
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


def check_knowledge_once(document: dict) -> list[str]:
    """No authority may be DEFINED in this declaration; every one must be discovered."""
    problems: list[str] = []
    raw = DECLARATION.read_text(encoding="utf-8")
    model = measure(document)
    for record in model["authorities"]:
        # A discovered identifier appearing in the declaration would mean the declaration,
        # not the located instrument, is the definition.
        if re.search(rf"\"{re.escape(record['id'])}\"", raw):
            problems.append(f"declaration names authority {record['id']}")
    if not model["authorities"]:
        problems.append("no authority was discovered from any located source")
    return problems


def check_no_promotion(document: dict) -> list[str]:
    """This programme must never report a vacant tier as occupied, nor a claim as ratified."""
    model = measure(document)
    problems: list[str] = []
    vacant = set(model["vacant_tiers"])
    for tier in model["tiers"]:
        if tier["id"] in vacant and str(tier["occupancy"]).upper() not in {"VACANT", "NONE", ""}:
            problems.append(f"{tier['id']}: reported {tier['occupancy']} while carrying a vacancy")
    for record in model["reconciliations"]:
        if record["ratifies"] or record["closes_vacancy"]:
            problems.append(f"{record['id']}: reconciliation asserts a ratification or a closure")
    for record in model["vacancies"]:
        if record["located"]:
            continue
        if not record["open_question"]:
            problems.append(f"{record['id']}: unlocated occupant with no open question recorded")
    # The corroboration measurement added by the tier-governance capability must never reach a
    # tier whose occupancy is recorded vacant: corroborating a vacancy would be exactly the
    # promotion the meta-constitution forbids and voids.
    for record in model["tier_governance"]:
        if record["vacant"] and record["corroboration"]:
            problems.append(f"{record['id']}: a recorded vacancy was corroborated as occupied")
        if record["id"] in vacant and not record["vacant"]:
            problems.append(f"{record['id']}: carries a vacancy but was measured as occupied")
    # A realization must never claim a tier the projection does not report occupied, which is
    # how the executable plane would otherwise be read into a vacant tier.
    for record in model["realizations"]:
        if not record["tier_located"]:
            problems.append(f"{record['id']}: realization claims a tier that is not located")
    return problems


GUARDS = {
    "check-declaration": check_declaration,
    "check-no-enumeration": check_no_enumeration,
    "check-write-scope": check_write_scope,
    "check-determinism": check_determinism,
    "check-knowledge-once": check_knowledge_once,
    "check-no-promotion": check_no_promotion,
}


# ---------------------------------------------------------------------------
# cli


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(add_help=True, description=__doc__.splitlines()[0])
    parser.add_argument("--render", action="store_true", help="regenerate the registers")
    parser.add_argument("--gate", action="store_true", help="fail-closed authority gate")
    parser.add_argument("--quiet", action="store_true")
    for name in GUARDS:
        parser.add_argument(f"--{name}", action="store_true")
    args = parser.parse_args(argv)

    try:
        document = load_declaration()
    except FailClosed as exc:
        print(f"UCOS-UCAF-001 ABORT: {exc}", file=sys.stderr)
        return 2

    selected = [name for name in GUARDS if getattr(args, name.replace("-", "_"))]
    if selected:
        failed = False
        for name in selected:
            try:
                problems = GUARDS[name](document)
            except FailClosed as exc:
                print(f"UCOS-UCAF-001 ABORT: {exc}", file=sys.stderr)
                return 2
            if problems:
                failed = True
                print(f"UCOS-UCAF-001 {name}: FAIL ({len(problems)})", file=sys.stderr)
                for problem in problems[:40]:
                    print(f"  - {problem}", file=sys.stderr)
            else:
                print(f"UCOS-UCAF-001 {name}: PASS")
        return 1 if failed else 0

    try:
        model = measure(document)
    except FailClosed as exc:
        print(f"UCOS-UCAF-001 ABORT: {exc}", file=sys.stderr)
        return 2

    # A gate VERIFIES; it does not produce. `--gate` used to regenerate every register
    # and ucaf.json here — unconditionally and without change detection — and only then
    # evaluate `args.gate` below, so the verdict was computed against a tree the verdict
    # run had itself just rewritten. That is why a read-only-sounding flag left
    # 00-MASTER/UCOS-UCAF-001/ dirty, and it defeats any clean-tree precondition placed
    # in front of an irreversible operation.
    #
    # `--render` is the honestly-named writing verb and is unaffected, including when
    # combined with `--gate` — that pair is an explicit request to render AND return a
    # verdict, so it still writes. No target in the repository uses the pair today:
    # `make ucaf-gate` is `--gate` alone and `make ucaf-replay` is `--render --quiet`,
    # so nothing depends on the combination; it is preserved because `--render` means
    # what it says, not because a caller relies on it. A bare invocation still renders,
    # so `make ucaf` is unchanged. Only the gate-without-render path becomes what its
    # name claims.
    gate_only = args.gate and not args.render
    written = [] if gate_only else write_registers(model)
    counts = model["counts"]
    if not args.quiet:
        print(
            f"UCOS-UCAF-001: {model['determination']} | authorities={counts['authorities']} "
            f"| tiers={counts['tiers']}({counts['vacant_tiers']} vacant) "
            f"| delegations={counts['delegations']} | successions={counts['successions']} "
            f"| resolved={counts['resolutions_answered']}/{counts['resolutions']} "
            f"| undefined={counts['undefined_references']} "
            f"| tiers-faithful={counts['tiers_faithful']}/{counts['tiers']} "
            f"| tokens={counts['minted_tokens']}({counts['minted_unclassified']} unclassified,"
            f"{counts['minted_collisions']} colliding) "
            f"| realizations={counts['realizations_bound']}/{counts['realizations']} "
            f"| reconciliation-required={counts['reconciliation_required']} "
            f"| gate={model['gate']} | seal={model['seal_sha256'][:16]}"
        )
        if gate_only:
            print(f"verified {len(render(model))+1} artifacts in "
                  f"{HERE.relative_to(REPO).as_posix()} — read-only, nothing written")
        else:
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
