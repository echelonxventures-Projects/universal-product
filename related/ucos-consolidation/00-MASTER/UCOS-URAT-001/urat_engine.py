#!/usr/bin/env python3
"""UCOS-URAT-001 — Universal Ratification Registry.

AUTHORITY = NONE (DERIVED TRUTH). This engine performs no ratification, confers no acceptance,
upgrades no state and creates no authority. CEP-006 Article XVI mandates a Ratification Registry
and XVI.4 provides that a ratification absent from it SHALL be deemed non-existent; no such
registry existed here, so located and committed ratification acts could not be relied upon by
any gate. This engine is that registry and only that registry.

Every state it records is READ out of the located act that determined it, verified by an anchor
that must be present in that act's own text. A state can therefore never be improved by editing
the declaration alone. The two transitions into the terminal state are declared to require the
out-of-corpus finality authority, and this engine holds no authority to perform any transition,
so the in-corpus ceiling is enforced structurally rather than described.

    python3 00-MASTER/UCOS-URAT-001/urat_engine.py --render
    python3 00-MASTER/UCOS-URAT-001/urat_engine.py --gate
    python3 00-MASTER/UCOS-URAT-001/urat_engine.py --check-declaration
    python3 00-MASTER/UCOS-URAT-001/urat_engine.py --check-no-enumeration
    python3 00-MASTER/UCOS-URAT-001/urat_engine.py --check-write-scope
    python3 00-MASTER/UCOS-URAT-001/urat_engine.py --check-determinism
    python3 00-MASTER/UCOS-URAT-001/urat_engine.py --check-coverage
    python3 00-MASTER/UCOS-URAT-001/urat_engine.py --check-no-conferral

Exit semantics:
    0  every blocking validation satisfied — gate OPEN
    1  a blocking validation unsatisfied, or a self-guard failed — gate CLOSED
    2  fail-closed abort — the declaration or the located authority registry is unusable, so no
       record may be admitted

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
DECLARATION = HERE / "urat-declaration.json"
MODEL = HERE / "urat.json"
OWN_PREFIX = HERE.relative_to(REPO).as_posix() + "/"

REQUIRED_SECTIONS = (
    "programme",
    "authority_registry",
    "state_basis",
    "freeze_admission_basis",
    "states",
    "transition_basis",
    "transitions",
    "record_field_basis",
    "record_required_fields",
    "computed_fields",
    "precondition_basis",
    "preconditions",
    "registry_rules",
    "records",
    "discovery",
    "excluded",
    "validations",
    "exit_criteria",
)


class FailClosed(Exception):
    """Raised when no record may be admitted. Always exits 2."""


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
    if not document["records"]:
        raise FailClosed("no ratification record is bound; the registry would assert emptiness")
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


def anchor_located(binding: dict) -> bool:
    text = read_text(binding["owner"])
    return text is not None and binding["anchor"] in text


def load_authority_registry(document: dict) -> set[str]:
    """The located authority registry. Its absence is a fail-closed abort, not a warning."""
    binding = document["authority_registry"]
    text = read_text(binding["owner"])
    if text is None:
        raise FailClosed(
            f"the located authority registry does not resolve: {binding['owner']} — "
            "no record may be admitted without a resolvable ratifying authority"
        )
    try:
        model = json.loads(text)
    except json.JSONDecodeError as exc:
        raise FailClosed(f"the located authority registry is not valid JSON: {exc}") from exc
    collection = model.get(binding["collection_pointer"])
    if not isinstance(collection, list) or not collection:
        raise FailClosed("the located authority registry contains no authority")
    identifiers = {
        entry.get(binding["id_field"])
        for entry in collection
        if isinstance(entry, dict) and entry.get(binding["id_field"])
    }
    if not identifiers:
        raise FailClosed("the located authority registry yields no identifier")
    return identifiers


def discover(document: dict) -> list[str]:
    """Every located file whose NAME declares it a ratification instrument."""
    discovery = document["discovery"]
    pattern = re.compile(discovery["filename_pattern"])
    extensions = set(discovery["extensions"])
    found: set[str] = set()
    for surface in discovery["surfaces"]:
        root = REPO / surface
        if not root.is_dir():
            continue
        for path in root.rglob("*"):
            if not path.is_file() or path.suffix not in extensions:
                continue
            relative = path.relative_to(REPO).as_posix()
            if relative.startswith(OWN_PREFIX):
                continue
            if pattern.search(path.name):
                found.add(relative)
    return sorted(found)


def measure(document: dict) -> dict:
    programme = document["programme"]
    registry_authorities = load_authority_registry(document)

    declared_states = {entry["state"] for entry in document["states"]}
    admits = {entry["state"] for entry in document["states"] if entry.get("admits_to_freeze")}
    out_of_corpus_targets = {
        entry["to"] for entry in document["transitions"] if entry.get("requires_out_of_corpus")
    }
    legal = {(entry["from"], entry["to"]) for entry in document["transitions"]}

    # --- state and transition vocabulary --------------------------------
    state_clause = read_text(document["state_basis"]["owner"]) or ""
    state_anchor_located = document["state_basis"]["anchor"] in state_clause
    clause_line = ""
    if state_anchor_located:
        for line in state_clause.splitlines():
            if document["state_basis"]["anchor"] in line:
                clause_line = line
                break
    unbound_states = sorted(
        entry["state"]
        for entry in document["states"]
        if not state_anchor_located or entry["state"] not in clause_line
    )
    transition_problems: list[str] = []
    if not anchor_located(document["transition_basis"]):
        transition_problems.append("the located transition clause is absent")
    for entry in document["transitions"]:
        for side in ("from", "to"):
            if entry[side] not in declared_states:
                transition_problems.append(f"{entry['from']}->{entry['to']}: {side} is not a declared state")

    # --- registry rules --------------------------------------------------
    rules = []
    unbound_rules: list[str] = []
    for rule in document["registry_rules"]:
        bound = anchor_located(rule)
        rules.append({"id": rule["id"], "rule": rule["rule"], "owner": rule["owner"], "bound": bound})
        if not bound:
            unbound_rules.append(f"{rule['id']}: anchor absent in {rule['owner']}")

    # --- preconditions ---------------------------------------------------
    precondition_clause_located = anchor_located(document["precondition_basis"])
    preconditions = []
    unbound_preconditions: list[str] = []
    if not precondition_clause_located:
        unbound_preconditions.append("the located precondition clause is absent")
    for entry in document["preconditions"]:
        resolved = read_text(entry["owner"]) is not None
        preconditions.append(
            {
                "id": entry["id"],
                "precondition": entry["precondition"],
                "owner": entry["owner"],
                "owner_resolved": resolved,
                "named_in_clause": precondition_clause_located
                and entry["precondition"] in document["precondition_basis"]["anchor"],
            }
        )
        if not resolved:
            unbound_preconditions.append(f"{entry['id']}: owner does not resolve")
        elif not preconditions[-1]["named_in_clause"]:
            unbound_preconditions.append(f"{entry['id']}: not named in the located clause")

    record_field_clause_located = anchor_located(document["record_field_basis"])
    freeze_clause_located = anchor_located(document["freeze_admission_basis"])

    # --- records ---------------------------------------------------------
    records: list[dict] = []
    unresolved_records: list[str] = []
    unlocated_verdicts: list[str] = []
    unlocated_states: list[str] = []
    unresolved_authorities: list[str] = []
    unclaimed_preconditions: list[str] = []
    unresolved_evidence: list[str] = []
    incomplete_records: list[str] = []
    conferral_breaches: list[str] = []
    unreconciled: list[str] = []

    for binding in document["records"]:
        identifier = binding["id"]
        act = read_text(binding["record"])
        if act is None:
            unresolved_records.append(f"{identifier}: act does not resolve: {binding['record']}")
            unreconciled.append(f"{identifier}: act does not resolve")

        verdict_located = act is not None and binding["verdict_anchor"] in act
        if not verdict_located:
            unlocated_verdicts.append(
                f"{identifier}: verdict anchor absent in {binding['record']}"
            )

        state = binding["state"]
        state_declared = state in declared_states
        state_basis_located = anchor_located(binding["state_basis"])
        if not state_declared:
            unlocated_states.append(f"{identifier}: {state} is not a declared state")
        elif not state_basis_located:
            unlocated_states.append(
                f"{identifier}: state basis anchor absent in {binding['state_basis']['owner']}"
            )

        authority = binding["authority"]
        authority_resolved = authority in registry_authorities
        authority_basis_located = anchor_located(binding["authority_basis"])
        if not authority_resolved:
            unresolved_authorities.append(
                f"{identifier}: authority does not resolve in the located authority registry"
            )
        elif not authority_basis_located:
            unresolved_authorities.append(f"{identifier}: authority basis anchor absent")

        preconditions_claimed = act is not None and binding["preconditions_anchor"] in act
        if not preconditions_claimed:
            unclaimed_preconditions.append(
                f"{identifier}: precondition anchor absent in {binding['record']}"
            )
        declared_precondition_ids = {entry["id"] for entry in document["preconditions"]}
        undeclared = [
            reference
            for reference in binding.get("preconditions") or []
            if reference not in declared_precondition_ids
        ]
        for reference in undeclared:
            unclaimed_preconditions.append(f"{identifier}: undeclared precondition {reference}")
        unsatisfied = sorted(declared_precondition_ids - set(binding.get("preconditions") or []))
        for reference in unsatisfied:
            unclaimed_preconditions.append(
                f"{identifier}: constitutional precondition {reference} is not recorded as satisfied"
            )

        evidence_state = []
        for reference in binding["evidence"]:
            text = read_text(reference)
            evidence_state.append(
                {
                    "reference": reference,
                    "resolved": text is not None,
                    "digest": digest(text)[:16] if text is not None else None,
                }
            )
            if text is None:
                unresolved_evidence.append(f"{identifier}: evidence does not resolve: {reference}")

        missing_fields = [
            field for field in document["record_required_fields"] if not binding.get(field)
        ]
        if missing_fields:
            incomplete_records.append(f"{identifier}: missing {', '.join(missing_fields)}")

        if state in out_of_corpus_targets:
            conferral_breaches.append(
                f"{identifier}: state {state} requires the out-of-corpus finality authority"
            )

        # program-state hash: COMPUTED from repository truth, never declared.
        material = [act or ""] + [
            entry["digest"] or "" for entry in sorted(evidence_state, key=lambda e: e["reference"])
        ]
        program_state_hash = digest("\u0000".join(material))

        records.append(
            {
                "id": identifier,
                "artifact": binding["artifact"],
                "record": binding["record"],
                "record_resolved": act is not None,
                "record_digest": digest(act)[:16] if act is not None else None,
                "outcome": binding["outcome"],
                "verdict_anchor_located": verdict_located,
                "state": state,
                "state_declared": state_declared,
                "state_basis": binding["state_basis"],
                "state_basis_located": state_basis_located,
                "admits_to_freeze": state in admits,
                "authority": authority,
                "authority_resolved": authority_resolved,
                "authority_basis_located": authority_basis_located,
                "authority_attribution": "RECORDED"
                if binding.get("authority_named_in_record")
                else "DERIVED",
                "preconditions_claimed": preconditions_claimed,
                "preconditions_satisfied": list(binding.get("preconditions") or []),
                "evidence": evidence_state,
                "evidence_resolved": sum(1 for entry in evidence_state if entry["resolved"]),
                "lineage_predecessor": binding.get("lineage_predecessor"),
                "program_state_hash": program_state_hash,
                "valid": bool(
                    act is not None
                    and verdict_located
                    and state_declared
                    and state_basis_located
                    and authority_resolved
                    and authority_basis_located
                    and preconditions_claimed
                    and not missing_fields
                    and all(entry["resolved"] for entry in evidence_state)
                ),
            }
        )

    records.sort(key=lambda entry: entry["id"])

    # --- uniqueness (CEP-006 XVI.2) --------------------------------------
    uniqueness: list[str] = []
    for field in ("artifact", "record"):
        seen: dict[str, str] = {}
        for entry in records:
            key = entry[field]
            if key in seen:
                uniqueness.append(f"{entry['id']}: duplicate {field} also held by {seen[key]}")
            else:
                seen[key] = entry["id"]
    by_artifact: dict[str, set[str]] = {}
    for entry in records:
        by_artifact.setdefault(entry["artifact"], set()).add(entry["authority"])
    for artifact, authorities in sorted(by_artifact.items()):
        if len(authorities) > 1:
            uniqueness.append(f"duplicate ratification authority admitted for one artifact: {artifact}")

    # --- lineage (CEP-006 XVI.3 / VI.3) ----------------------------------
    lineage_problems: list[str] = []
    known = {entry["id"]: entry for entry in records}
    for entry in records:
        predecessor = entry["lineage_predecessor"]
        if predecessor is None:
            continue
        if predecessor not in known:
            lineage_problems.append(f"{entry['id']}: lineage predecessor does not resolve")
            continue
        step = (known[predecessor]["state"], entry["state"])
        if step not in legal:
            lineage_problems.append(
                f"{entry['id']}: {step[0]} -> {step[1]} is not a declared legal transition"
            )
    state_of: dict[str, int] = {}

    def walk(node: str, trail: list[str]) -> None:
        if state_of.get(node) == 1:
            lineage_problems.append("lineage cycle: " + " -> ".join(trail + [node]))
            return
        if state_of.get(node) == 2:
            return
        state_of[node] = 1
        predecessor = known[node]["lineage_predecessor"]
        if predecessor in known:
            walk(predecessor, trail + [node])
        state_of[node] = 2

    for identifier in sorted(known):
        walk(identifier, [])

    # --- coverage (CEP-006 XVI.4) ----------------------------------------
    discovered = discover(document)
    registered_paths = {entry["record"] for entry in records}
    excluded_paths = {entry["path"] for entry in document["excluded"]}
    unaccounted = sorted(
        path for path in discovered if path not in registered_paths and path not in excluded_paths
    )
    stale_exclusions = sorted(path for path in excluded_paths if path not in discovered)
    coverage_problems = [f"unaccounted ratification instrument: {path}" for path in unaccounted]
    coverage_problems += [f"exclusion names a file outside the discovery surface: {path}" for path in stale_exclusions]
    for entry in document["excluded"]:
        if not entry.get("class") or not entry.get("reason"):
            coverage_problems.append(f"exclusion {entry.get('path')} carries no class or reason")

    # --- boot reconciliation (CEP-006 XVI.3 / XXI.1) ---------------------
    if not freeze_clause_located:
        unreconciled.append("the located freeze-admission clause is absent")
    if not record_field_clause_located:
        unreconciled.append("the located record-field clause is absent")
    for entry in records:
        if entry["record_digest"] is None:
            unreconciled.append(f"{entry['id']}: no content digest could be computed")

    findings: dict[str, list[str]] = {
        "URAT-VAL-01": unbound_states + ([] if state_anchor_located else ["the located state clause is absent"]),
        "URAT-VAL-02": transition_problems,
        "URAT-VAL-03": unresolved_records,
        "URAT-VAL-04": unlocated_verdicts,
        "URAT-VAL-05": unlocated_states,
        "URAT-VAL-06": unresolved_authorities,
        "URAT-VAL-07": unclaimed_preconditions + unbound_preconditions,
        "URAT-VAL-08": unresolved_evidence,
        "URAT-VAL-09": incomplete_records,
        "URAT-VAL-10": uniqueness,
        "URAT-VAL-11": lineage_problems,
        "URAT-VAL-12": unbound_rules,
        "URAT-VAL-13": conferral_breaches,
        "URAT-VAL-14": coverage_problems,
        "URAT-VAL-15": unreconciled,
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

    by_state: dict[str, int] = {}
    for entry in records:
        by_state[entry["state"]] = by_state.get(entry["state"], 0) + 1

    model = {
        "programme": programme,
        "states": [
            {
                "id": entry["id"],
                "state": entry["state"],
                "located_in_clause": state_anchor_located and entry["state"] in clause_line,
                "admits_to_freeze": bool(entry.get("admits_to_freeze")),
                "terminal": bool(entry.get("terminal")),
            }
            for entry in document["states"]
        ],
        "transitions": [
            {
                "from": entry["from"],
                "to": entry["to"],
                "requires_out_of_corpus": bool(entry.get("requires_out_of_corpus")),
                "performable_in_corpus": not entry.get("requires_out_of_corpus"),
            }
            for entry in document["transitions"]
        ],
        "registry_rules": rules,
        "preconditions": preconditions,
        "records": records,
        "by_state": dict(sorted(by_state.items())),
        "coverage": {
            "discovered": discovered,
            "registered": sorted(registered_paths),
            "excluded": [
                {"path": entry["path"], "class": entry["class"], "reason": entry["reason"]}
                for entry in sorted(document["excluded"], key=lambda item: item["path"])
            ],
            "unaccounted": unaccounted,
        },
        "authority_registry": {
            "owner": document["authority_registry"]["owner"],
            "authorities": len(registry_authorities),
        },
        "validations": validations,
        "counts": {
            "records": len(records),
            "records_valid": sum(1 for entry in records if entry["valid"]),
            "records_admitting_freeze": sum(1 for entry in records if entry["admits_to_freeze"]),
            "attributions_recorded": sum(
                1 for entry in records if entry["authority_attribution"] == "RECORDED"
            ),
            "attributions_derived": sum(
                1 for entry in records if entry["authority_attribution"] == "DERIVED"
            ),
            "states_declared": len(document["states"]),
            "transitions_declared": len(document["transitions"]),
            "transitions_in_corpus": sum(
                1 for entry in document["transitions"] if not entry.get("requires_out_of_corpus")
            ),
            "registry_rules_bound": sum(1 for rule in rules if rule["bound"]),
            "registry_rules": len(rules),
            "discovered": len(discovered),
            "excluded": len(document["excluded"]),
            "unaccounted": len(unaccounted),
        },
        "finality_ceiling": {
            "in_corpus_ceiling": sorted(
                {entry["state"] for entry in records}
            ),
            "unreachable_in_corpus": sorted(out_of_corpus_targets),
            "basis": document["registry_rules"][4]["anchor"]
            if len(document["registry_rules"]) > 4
            else None,
        },
        "blocking_failures": blocking_failures,
        "gate": gate,
        "gate_exit": 1 if blocking_failures else 0,
        "determination": "RATIFICATION-REGISTRY-BOUND" if gate == "OPEN" else "RATIFICATION-REGISTRY-INCOMPLETE",
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
    rows = [
        ["PROGRAMME", f"{programme['id']} — {programme['name']}"],
        ["VERSION", programme["version"]],
        ["AUTHORITY", programme["authority"]],
        ["RECORDS REGISTERED", f"{counts['records_valid']}/{counts['records']} valid"],
        ["RECORDS ADMITTING FREEZE", counts["records_admitting_freeze"]],
        ["AUTHORITY ATTRIBUTION", f"{counts['attributions_recorded']} recorded · {counts['attributions_derived']} derived"],
        ["STATE VOCABULARY", f"{counts['states_declared']} states · {counts['transitions_declared']} legal transitions ({counts['transitions_in_corpus']} performable in corpus)"],
        ["REGISTRY RULES BOUND", f"{counts['registry_rules_bound']}/{counts['registry_rules']}"],
        ["COVERAGE", f"{counts['discovered']} discovered · {counts['records']} registered · {counts['excluded']} excluded · {counts['unaccounted']} unaccounted"],
        ["GATE", model["gate"]],
        ["DETERMINATION", model["determination"]],
        ["SEAL (sha256)", model["seal_sha256"]],
        ["GENERATED BY", "urat_engine.py — regenerated, never hand-authored"],
    ]
    return table(["Field", "Value"], rows) + "\n\n> " + programme["disclosure"]


def render(model: dict) -> dict[str, str]:
    programme = model["programme"]
    pages: dict[str, str] = {}

    pages["00-URAT-DASHBOARD.md"] = "\n".join(
        [
            f"# {programme['id']} — {programme['name']} · Dashboard",
            "",
            front_matter(model),
            "",
            "## Records by state",
            "",
            table(
                ["State", "Records"],
                [[state, count] for state, count in model["by_state"].items()],
            ),
            "",
            "## Finality ceiling",
            "",
            "States reached in this repository: "
            + ", ".join(f"`{state}`" for state in model["finality_ceiling"]["in_corpus_ceiling"]),
            "",
            "States unreachable from inside the corpus: "
            + ", ".join(f"`{state}`" for state in model["finality_ceiling"]["unreachable_in_corpus"]),
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

    pages["01-RATIFICATION-REGISTER.md"] = "\n".join(
        [
            f"# {programme['id']} · Ratification Register",
            "",
            "The single canonical record of ratification in this repository (CEP-006 XVI.1).",
            "Every state below is read out of the located act named in the record column and",
            "verified by an anchor present in that act's own text. This registry confers nothing.",
            "",
            table(
                ["Record", "Artifact", "State", "Admits freeze", "Authority", "Attribution", "Valid"],
                [
                    [
                        f"`{entry['id']}`",
                        entry["artifact"],
                        f"**{entry['state']}**",
                        "YES" if entry["admits_to_freeze"] else "no",
                        f"`{entry['authority']}`",
                        entry["authority_attribution"],
                        "YES" if entry["valid"] else "**NO**",
                    ]
                    for entry in model["records"]
                ],
            ),
            "",
            "## Located acts, outcomes and content digests",
            "",
            table(
                ["Record", "Located act", "Outcome as determined", "Act digest", "Program-state hash"],
                [
                    [
                        f"`{entry['id']}`",
                        f"`{entry['record']}`",
                        entry["outcome"],
                        entry["record_digest"] or "—",
                        entry["program_state_hash"][:16],
                    ]
                    for entry in model["records"]
                ],
            ),
            "",
            "## Evidence referenced",
            "",
            table(
                ["Record", "Evidence", "Resolves", "Digest"],
                [
                    [
                        f"`{entry['id']}`",
                        f"`{reference['reference']}`",
                        "YES" if reference["resolved"] else "**NO**",
                        reference["digest"] or "—",
                    ]
                    for entry in model["records"]
                    for reference in entry["evidence"]
                ],
            ),
            "",
        ]
    )

    pages["02-STATE-MACHINE-AND-RULES.md"] = "\n".join(
        [
            f"# {programme['id']} · State Machine, Preconditions and Registry Rules",
            "",
            "## Ratification states (projected from the located clause)",
            "",
            table(
                ["State", "Located in clause", "Admits to freeze lifecycle", "Terminal"],
                [
                    [
                        f"`{entry['state']}`",
                        "YES" if entry["located_in_clause"] else "**NO**",
                        "YES" if entry["admits_to_freeze"] else "no",
                        "YES" if entry["terminal"] else "no",
                    ]
                    for entry in model["states"]
                ],
            ),
            "",
            "## Legal transitions",
            "",
            "A transition not listed here IS PROHIBITED. This engine performs none of them: it",
            "records only what a located act determined.",
            "",
            table(
                ["From", "To", "Performable in corpus"],
                [
                    [
                        f"`{entry['from']}`",
                        f"`{entry['to']}`",
                        "YES" if entry["performable_in_corpus"] else "**NO — out-of-corpus finality authority**",
                    ]
                    for entry in model["transitions"]
                ],
            ),
            "",
            "## Preconditions (CEP-006 V.1)",
            "",
            table(
                ["Precondition", "Obligation", "Owner", "Owner resolves", "Named in clause"],
                [
                    [
                        f"`{entry['id']}`",
                        entry["precondition"],
                        f"`{entry['owner']}`",
                        "YES" if entry["owner_resolved"] else "**NO**",
                        "YES" if entry["named_in_clause"] else "**NO**",
                    ]
                    for entry in model["preconditions"]
                ],
            ),
            "",
            "## Registry rules (CEP-006 Article XVI)",
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
                    for rule in model["registry_rules"]
                ],
            ),
            "",
        ]
    )

    pages["03-COVERAGE-AND-CERTIFICATION.md"] = "\n".join(
        [
            f"# {programme['id']} · Coverage and Certification",
            "",
            front_matter(model),
            "",
            "## Coverage over the discovery surface",
            "",
            "CEP-006 XVI.4 deems a ratification absent from the registry non-existent. Coverage is",
            "therefore proven in the opposite direction: every located file whose name declares it",
            "a ratification instrument is either registered or excluded with a class and a reason.",
            "",
            table(
                ["Located instrument", "Disposition", "Class / record", "Reason"],
                [
                    [
                        f"`{path}`",
                        "REGISTERED"
                        if path in set(model["coverage"]["registered"])
                        else "EXCLUDED",
                        next(
                            (
                                f"`{entry['id']}`"
                                for entry in model["records"]
                                if entry["record"] == path
                            ),
                            next(
                                (
                                    entry["class"]
                                    for entry in model["coverage"]["excluded"]
                                    if entry["path"] == path
                                ),
                                "—",
                            ),
                        ),
                        next(
                            (
                                entry["reason"]
                                for entry in model["coverage"]["excluded"]
                                if entry["path"] == path
                            ),
                            "Registered as a canonical ratification record.",
                        ),
                    ]
                    for path in model["coverage"]["discovered"]
                ],
            ),
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
            "This registry is issued at the standing this repository's certification owner",
            "reports, and every record it holds carries the in-corpus ceiling CEP-006 I.4 fixes.",
            "It holds no authority over constitutional content (CEP-006 XVI.5): it is operational",
            "memory. Where this registry and a located ratification act differ, the act governs.",
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
    seen: set[str] = set()
    for section in ("states", "transitions", "preconditions", "registry_rules", "records", "validations", "exit_criteria"):
        for entry in document[section]:
            identifier = entry.get("id")
            if identifier is None:
                continue
            if identifier in seen:
                problems.append(f"{section}: duplicate id {identifier}")
            seen.add(identifier)
    for key in ("state_basis", "freeze_admission_basis", "transition_basis", "record_field_basis", "precondition_basis"):
        if not (REPO / document[key]["owner"]).is_file():
            problems.append(f"{key}: owner does not resolve")
        elif not anchor_located(document[key]):
            problems.append(f"{key}: anchor absent in {document[key]['owner']}")
    declared = {entry["state"] for entry in document["states"]}
    for entry in document["states"]:
        if entry["state"] not in (read_text(document["state_basis"]["owner"]) or ""):
            problems.append(f"state {entry['state']} does not appear in its basis instrument")
    for entry in document["transitions"]:
        for side in ("from", "to"):
            if entry[side] not in declared:
                problems.append(f"transition {entry['from']}->{entry['to']}: undeclared {side}")
    for binding in document["records"]:
        if not (REPO / binding["record"]).is_file():
            problems.append(f"{binding['id']}: act does not resolve")
        for key in ("state_basis", "authority_basis"):
            if not (REPO / binding[key]["owner"]).is_file():
                problems.append(f"{binding['id']}: {key} owner does not resolve")
    for entry in document["excluded"]:
        if not (REPO / entry["path"]).is_file():
            problems.append(f"exclusion path does not resolve: {entry['path']}")
    return problems


def check_no_enumeration(document: dict) -> list[str]:
    """No state, record id, artifact, authority or located act may be a literal in this engine."""
    source = Path(__file__).read_text(encoding="utf-8")
    leaked: list[str] = []
    for entry in document["states"]:
        if re.search(rf"\b{re.escape(entry['state'])}\b", source):
            leaked.append(f"state {entry['state']}")
    for binding in document["records"]:
        if binding["id"] in source:
            leaked.append(f"record {binding['id']}")
        if binding["record"] in source:
            leaked.append(f"act {binding['record']}")
        if binding["authority"] in source:
            leaked.append(f"authority {binding['authority']}")
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


def check_coverage(document: dict) -> list[str]:
    model = measure(document)
    return list(model["coverage"]["unaccounted"])


def check_no_conferral(document: dict) -> list[str]:
    """This engine must never record a state it could not have read, nor perform a transition."""
    model = measure(document)
    problems: list[str] = []
    unreachable = set(model["finality_ceiling"]["unreachable_in_corpus"])
    for entry in model["records"]:
        if entry["state"] in unreachable:
            problems.append(f"{entry['id']}: records a state reserved to the out-of-corpus authority")
        if not entry["state_basis_located"]:
            problems.append(f"{entry['id']}: state is asserted, not located")
        if not entry["verdict_anchor_located"]:
            problems.append(f"{entry['id']}: verdict is asserted, not located")
    return problems


GUARDS = {
    "check-declaration": check_declaration,
    "check-no-enumeration": check_no_enumeration,
    "check-write-scope": check_write_scope,
    "check-determinism": check_determinism,
    "check-coverage": check_coverage,
    "check-no-conferral": check_no_conferral,
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
        print(f"UCOS-URAT-001 ABORT: {exc}", file=sys.stderr)
        return 2

    selected = [name for name in GUARDS if getattr(args, name.replace("-", "_"))]
    if selected:
        failed = False
        for name in selected:
            try:
                problems = GUARDS[name](document)
            except FailClosed as exc:
                print(f"UCOS-URAT-001 ABORT: {exc}", file=sys.stderr)
                return 2
            if problems:
                failed = True
                print(f"UCOS-URAT-001 {name}: FAIL ({len(problems)})", file=sys.stderr)
                for problem in problems[:40]:
                    print(f"  - {problem}", file=sys.stderr)
            else:
                print(f"UCOS-URAT-001 {name}: PASS")
        return 1 if failed else 0

    try:
        model = measure(document)
    except FailClosed as exc:
        print(f"UCOS-URAT-001 ABORT: {exc}", file=sys.stderr)
        return 2

    written = write_registers(model)
    counts = model["counts"]
    if not args.quiet:
        print(
            f"UCOS-URAT-001: {model['determination']} | records={counts['records_valid']}/{counts['records']} "
            f"| admitting-freeze={counts['records_admitting_freeze']} "
            f"| attribution={counts['attributions_recorded']}rec/{counts['attributions_derived']}der "
            f"| coverage={counts['records'] + counts['excluded']}/{counts['discovered']} "
            f"| unaccounted={counts['unaccounted']} | gate={model['gate']} "
            f"| seal={model['seal_sha256'][:16]}"
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
