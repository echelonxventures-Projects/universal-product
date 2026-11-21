#!/usr/bin/env python3
"""UCOS-UFEP-001 — Universal Freeze Eligibility Programme.

AUTHORITY = NONE (DERIVED TRUTH). This engine freezes nothing, seals no baseline, transitions no
artifact and holds no Freeze Authority.

CEP-007 Article IV makes freeze eligibility a decidable property of an artifact and Article V
fixes its five preconditions, each required to be machine-verifiable. Nothing in this repository
measured them together, and one of the five could not be measured at all until the ratification
registry CEP-006 mandates existed. This engine measures all five from the located determinations
and sealed machine models that own them, decides eligibility, computes the content-addressed
baseline a freeze would seal, verifies the located frozen baseline against its recorded manifest,
and determines repository-level constitutional completion from the same evidence.

Every state past eligibility is declared unreachable by this programme, and a self-guard fails
closed if any subject is ever reported in one — CEP-007 VII.1 reserves the freeze decision to
Freeze Authority and I.5 forbids its self-conferral by Execution Authority.

    python3 00-MASTER/UCOS-UFEP-001/ufep_engine.py --render
    python3 00-MASTER/UCOS-UFEP-001/ufep_engine.py --gate
    python3 00-MASTER/UCOS-UFEP-001/ufep_engine.py --check-declaration
    python3 00-MASTER/UCOS-UFEP-001/ufep_engine.py --check-no-enumeration
    python3 00-MASTER/UCOS-UFEP-001/ufep_engine.py --check-write-scope
    python3 00-MASTER/UCOS-UFEP-001/ufep_engine.py --check-determinism
    python3 00-MASTER/UCOS-UFEP-001/ufep_engine.py --check-no-freeze
    python3 00-MASTER/UCOS-UFEP-001/ufep_engine.py --check-no-drift

Exit semantics:
    0  every blocking validation satisfied — freeze eligibility and constitutional completion
       are both determined TRUE at the scope declared
    1  a blocking validation unsatisfied, or a self-guard failed
    2  fail-closed abort — the declaration is unusable, so no determination may be asserted

Stdlib only. No network. No timestamp, no duration, no commit identity and no absolute path is
emitted, so the sealed output set is byte-identical for an unchanged repository.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
DECLARATION = HERE / "ufep-declaration.json"
MODEL = HERE / "ufep.json"
OWN_PREFIX = HERE.relative_to(REPO).as_posix() + "/"

REQUIRED_SECTIONS = (
    "programme",
    "state_basis",
    "transition_basis",
    "states",
    "transitions",
    "eligibility_basis",
    "admission_basis",
    "decidability_basis",
    "unverifiable_basis",
    "finality_not_a_freeze_blocker_basis",
    "preconditions",
    "precondition_basis",
    "sources",
    "subjects",
    "baseline_basis",
    "freeze_record_fields",
    "freeze_record_basis",
    "drift_basis",
    "frozen_baselines",
    "authorizations",
    "completion_criteria",
    "validations",
    "exit_criteria",
)

CLAUSE_KEYS = (
    "state_basis",
    "transition_basis",
    "eligibility_basis",
    "admission_basis",
    "decidability_basis",
    "unverifiable_basis",
    "finality_not_a_freeze_blocker_basis",
    "precondition_basis",
    "baseline_basis",
    "freeze_record_basis",
    "drift_basis",
)

# Operators a declared source may use. An operator outside this set is a fail-closed violation.
OPERATORS = ("is_true", "equals", "count_zero", "count_max", "non_empty")

SATISFIED = "SATISFIED"
UNSATISFIED = "UNSATISFIED"


class FailClosed(Exception):
    """Raised when no determination may be asserted. Always exits 2."""


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
    if not document["subjects"]:
        raise FailClosed("no freeze subject is declared; eligibility would be vacuous")
    return document


def read_text(relative: str) -> str | None:
    target = REPO / relative
    if not target.is_file():
        return None
    try:
        return target.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return None


def read_json(relative: str) -> dict | None:
    text = read_text(relative)
    if text is None:
        return None
    try:
        document = json.loads(text)
    except json.JSONDecodeError:
        return None
    return document if isinstance(document, dict) else None


def digest(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def anchor_located(binding: dict) -> bool:
    text = read_text(binding["owner"])
    return text is not None and binding["anchor"] in text


def resolve_pointer(document: dict, pointer: str) -> object:
    current: object = document
    for part in pointer.split("."):
        if not isinstance(current, dict) or part not in current:
            return None
        current = current[part]
    return current


def evaluate(source: dict) -> dict:
    """Evaluate one declared source against its sealed machine model. Unreadable is UNSATISFIED."""
    operator = source.get("operator")
    if operator is not None and operator not in OPERATORS:
        raise FailClosed(f"source {source['id']} declares unknown operator {operator!r}")
    document = read_json(source["owner"])
    if document is None:
        return {
            "id": source["id"],
            "owner": source["owner"],
            "readable": False,
            "observed": None,
            "outcome": UNSATISFIED,
            "reason": "source does not resolve or is not a readable model",
        }
    observed = resolve_pointer(document, source["pointer"]) if source.get("pointer") else None
    if operator == "is_true":
        satisfied = observed is True
    elif operator == "equals":
        satisfied = observed == source.get("expect")
    elif operator == "count_zero":
        satisfied = isinstance(observed, list) and len(observed) == 0
    elif operator == "count_max":
        satisfied = isinstance(observed, list) and len(observed) <= int(source.get("expect", 0))
    elif operator == "non_empty":
        satisfied = bool(observed)
    else:
        satisfied = False
    return {
        "id": source["id"],
        "owner": source["owner"],
        "readable": True,
        "observed": observed if not isinstance(observed, (list, dict)) else len(observed),
        "outcome": SATISFIED if satisfied else UNSATISFIED,
        "reason": None if satisfied else "the observed value does not meet the declared expectation",
    }


def verify_manifest(entry: dict) -> dict:
    """CEP-007 X.2 no-drift guard over a located frozen baseline manifest."""
    text = read_text(entry["manifest"])
    if text is None:
        return {
            "id": entry["id"],
            "manifest": entry["manifest"],
            "readable": False,
            "entries": 0,
            "matched": 0,
            "missing": [],
            "drifted": [],
            "notice_located": False,
        }
    matched = 0
    missing: list[str] = []
    drifted: list[str] = []
    total = 0
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        recorded, _, path = stripped.partition("  ")
        if not path:
            continue
        total += 1
        target = REPO / path
        if not target.is_file():
            missing.append(path)
            continue
        try:
            actual = hashlib.sha256(target.read_bytes()).hexdigest()
        except OSError:
            missing.append(path)
            continue
        if actual == recorded:
            matched += 1
        else:
            drifted.append(path)
    return {
        "id": entry["id"],
        "manifest": entry["manifest"],
        "readable": True,
        "entries": total,
        "matched": matched,
        "missing": sorted(missing),
        "drifted": sorted(drifted),
        "notice_located": anchor_located({"owner": entry["notice"], "anchor": entry["notice_anchor"]}),
    }


def measure(document: dict) -> dict:
    programme = document["programme"]

    # --- clause bindings --------------------------------------------------
    clauses = []
    unbound_clauses: list[str] = []
    for key in CLAUSE_KEYS:
        binding = document[key]
        bound = anchor_located(binding)
        clauses.append({"key": key, "owner": binding["owner"], "bound": bound})
        if not bound:
            unbound_clauses.append(f"{key}: anchor absent in {binding['owner']}")

    declared_states = {entry["state"] for entry in document["states"]}
    reachable = {
        entry["state"] for entry in document["states"] if entry.get("reachable_by_this_programme")
    }
    state_clause = read_text(document["state_basis"]["owner"]) or ""
    state_problems = [
        f"{entry['state']}: absent from the located state clause"
        for entry in document["states"]
        if entry["state"] not in state_clause
    ]
    for entry in document["transitions"]:
        for side in ("from", "to"):
            if entry[side] not in declared_states:
                state_problems.append(f"transition {entry['from']}->{entry['to']}: undeclared {side}")

    initial = [entry["state"] for entry in document["states"] if entry.get("initial")]
    if len(initial) != 1:
        state_problems.append("exactly one initial freeze state must be declared")
    initial_state = initial[0] if initial else None
    eligible_state = next(
        (
            entry["to"]
            for entry in document["transitions"]
            if entry["from"] == initial_state and not entry.get("requires_freeze_authority")
        ),
        None,
    )
    if eligible_state is None:
        raise FailClosed("no transition from the initial state is performable without Freeze Authority")

    # --- located ratification registry ------------------------------------
    ratification_source = next(
        (entry for entry in document["sources"] if entry.get("records_pointer")), None
    )
    if ratification_source is None:
        raise FailClosed("no ratification registry source is declared")
    registry = read_json(ratification_source["owner"])
    records: dict[str, dict] = {}
    if registry is not None:
        for entry in registry.get(ratification_source["records_pointer"]) or []:
            if isinstance(entry, dict) and entry.get(ratification_source["id_field"]):
                records[entry[ratification_source["id_field"]]] = entry

    # --- repository-scope preconditions -----------------------------------
    source_by_id = {entry["id"]: entry for entry in document["sources"]}
    evaluations = {
        entry["id"]: evaluate(entry)
        for entry in document["sources"]
        if entry.get("operator")
    }
    traceability = evaluations.get("UFEP-SRC-TRACEABILITY")
    determinism = evaluations.get("UFEP-SRC-DETERMINISM")

    repository_preconditions: dict[str, dict] = {}
    for entry in document["preconditions"]:
        if entry["scope"] != "repository":
            continue
        # bind by ordinal position among repository-scope preconditions to the declared sources
        repository_preconditions[entry["id"]] = entry

    # The two repository-scope preconditions are the traceability obligation and the
    # determinism proof, in the order CEP-007 V.1 states them; both are read from sealed models.
    repository_outcomes: dict[str, dict] = {}
    ordered_repository = [entry for entry in document["preconditions"] if entry["scope"] == "repository"]
    ordered_sources = [traceability, determinism]
    for entry, evaluation in zip(ordered_repository, ordered_sources):
        if evaluation is None:
            repository_outcomes[entry["id"]] = {
                "outcome": UNSATISFIED,
                "reason": "no sealed model is declared for this precondition",
                "owner": None,
            }
        else:
            repository_outcomes[entry["id"]] = {
                "outcome": evaluation["outcome"],
                "reason": evaluation["reason"],
                "owner": evaluation["owner"],
            }

    # --- subjects ----------------------------------------------------------
    subject_scoped = [entry for entry in document["preconditions"] if entry["scope"] == "subject"]
    if len(subject_scoped) < 3:
        raise FailClosed("the subject-scope precondition set is incomplete")
    validation_precondition, certification_precondition, ratification_precondition = subject_scoped[:3]

    subjects: list[dict] = []
    unmeasured: list[str] = []
    undecidable: list[str] = []
    unratified: list[str] = []
    incomplete_records: list[str] = []
    baseline_problems: list[str] = []
    unreachable_states: list[str] = []

    for entry in document["subjects"]:
        identifier = entry["id"]
        record = records.get(entry["ratification_record"])
        outcomes: dict[str, dict] = {}

        validation_text = read_text(entry["validation_evidence"]["owner"])
        validation_ok = validation_text is not None and (
            entry["validation_evidence"]["anchor"] in validation_text
        )
        outcomes[validation_precondition["id"]] = {
            "outcome": SATISFIED if validation_ok else UNSATISFIED,
            "owner": entry["validation_evidence"]["owner"],
            "reason": None if validation_ok else "the located determination does not carry the declared verdict",
        }

        certification_text = read_text(entry["certification_evidence"]["owner"])
        certification_ok = certification_text is not None and (
            entry["certification_evidence"]["anchor"] in certification_text
        )
        outcomes[certification_precondition["id"]] = {
            "outcome": SATISFIED if certification_ok else UNSATISFIED,
            "owner": entry["certification_evidence"]["owner"],
            "reason": None if certification_ok else "the located determination does not carry the declared verdict",
        }

        admits = bool(record and record.get(ratification_source["admits_field"]))
        record_valid = bool(record and record.get(ratification_source["valid_field"]))
        ratification_ok = admits and record_valid
        outcomes[ratification_precondition["id"]] = {
            "outcome": SATISFIED if ratification_ok else UNSATISFIED,
            "owner": ratification_source["owner"],
            "reason": None
            if ratification_ok
            else "no valid record in the located ratification registry admits this artifact to the freeze lifecycle",
        }
        if not ratification_ok:
            unratified.append(f"{identifier}: {outcomes[ratification_precondition['id']]['reason']}")

        for precondition_id, outcome in repository_outcomes.items():
            outcomes[precondition_id] = dict(outcome)

        for precondition in document["preconditions"]:
            if precondition["id"] not in outcomes:
                unmeasured.append(f"{identifier}: {precondition['id']} was not measured")

        unsatisfied = sorted(
            key for key, value in outcomes.items() if value["outcome"] != SATISFIED
        )
        state = eligible_state if not unsatisfied else initial_state
        if state not in reachable:
            unreachable_states.append(f"{identifier}: {state}")

        # --- baseline (CEP-007 VIII.2), computed from located material only
        artifact_text = read_text(record[ratification_source["record_field"]]) if record else None
        evidence_digests: list[str] = []
        if record:
            for reference in record.get("evidence") or []:
                if isinstance(reference, dict) and reference.get("digest"):
                    evidence_digests.append(str(reference["digest"]))
        material = [
            artifact_text or "",
            "\u0000".join(sorted(evidence_digests)),
            str(record.get("program_state_hash")) if record else "",
        ]
        baseline_digest = digest("\u0001".join(material))
        if artifact_text is None:
            baseline_problems.append(f"{identifier}: the ratified act does not resolve, so no baseline is computable")

        freeze_record = {
            "artifact": record.get(ratification_source["artifact_field"]) if record else None,
            "preconditions": [key for key, value in sorted(outcomes.items()) if value["outcome"] == SATISFIED],
            "baseline_digest": baseline_digest,
            "version": baseline_digest[:12],
            "lineage": record.get("lineage_predecessor") if record else None,
            "state": state,
        }
        missing_fields = [
            field
            for field in document["freeze_record_fields"]
            if field != "lineage" and not freeze_record.get(field)
        ]
        if missing_fields:
            incomplete_records.append(f"{identifier}: missing {', '.join(missing_fields)}")

        if state not in (initial_state, eligible_state):
            undecidable.append(f"{identifier}: resolved to {state}")

        subjects.append(
            {
                "id": identifier,
                "artifact": freeze_record["artifact"],
                "ratification_record": entry["ratification_record"],
                "ratification_state": record.get(ratification_source["state_field"]) if record else None,
                "located_act": record.get(ratification_source["record_field"]) if record else None,
                "preconditions": {key: outcomes[key] for key in sorted(outcomes)},
                "unsatisfied": unsatisfied,
                "state": state,
                "eligible": state == eligible_state,
                "freeze_record": freeze_record,
            }
        )

    subjects.sort(key=lambda item: item["id"])

    # --- baseline reproducibility -----------------------------------------
    reproduced = {}
    for item in subjects:
        reproduced[item["id"]] = item["freeze_record"]["baseline_digest"]

    # --- subject coverage over the registry -------------------------------
    declared_records = {entry["ratification_record"] for entry in document["subjects"]}
    uncovered = sorted(
        identifier
        for identifier, record in records.items()
        if record.get(ratification_source["valid_field"]) and identifier not in declared_records
    )

    # --- no-drift over located frozen baselines ---------------------------
    manifests = [verify_manifest(entry) for entry in document["frozen_baselines"]]
    drift_problems: list[str] = []
    for entry in manifests:
        if not entry["readable"]:
            drift_problems.append(f"{entry['id']}: manifest does not resolve")
            continue
        if not entry["notice_located"]:
            drift_problems.append(f"{entry['id']}: the freeze notice does not carry its declared status")
        drift_problems.extend(f"{entry['id']}: drifted {path}" for path in entry["drifted"])
        drift_problems.extend(f"{entry['id']}: missing {path}" for path in entry["missing"])

    # --- authorizations ---------------------------------------------------
    authorizations = []
    unlocated_authorizations: list[str] = []
    for entry in document["authorizations"]:
        located = anchor_located(entry)
        authorizations.append(
            {
                "id": entry["id"],
                "authorization": entry["authorization"],
                "owner": entry["owner"],
                "located": located,
                "acted_on": bool(entry.get("acted_on_by_this_programme")),
            }
        )
        if not located:
            unlocated_authorizations.append(f"{entry['id']}: anchor absent in {entry['owner']}")

    # --- completion criteria ----------------------------------------------
    completion = []
    unmeasured_criteria: list[str] = []
    for entry in document["completion_criteria"]:
        source = source_by_id.get(entry["source"])
        evaluation = evaluations.get(entry["source"]) if source else None
        if evaluation is None:
            unmeasured_criteria.append(f"{entry['id']}: source {entry['source']} is not evaluable")
            completion.append(
                {
                    "id": entry["id"],
                    "criterion": entry["criterion"],
                    "source": entry["source"],
                    "owner": source["owner"] if source else None,
                    "outcome": UNSATISFIED,
                    "blocking": bool(entry["blocking"]),
                }
            )
            continue
        completion.append(
            {
                "id": entry["id"],
                "criterion": entry["criterion"],
                "source": entry["source"],
                "owner": evaluation["owner"],
                "observed": evaluation["observed"],
                "outcome": evaluation["outcome"],
                "blocking": bool(entry["blocking"]),
            }
        )

    ineligible = [item["id"] for item in subjects if not item["eligible"]]
    unmet_completion = [
        entry["id"] for entry in completion if entry["blocking"] and entry["outcome"] != SATISFIED
    ]

    findings: dict[str, list[str]] = {
        "UFEP-VAL-01": unbound_clauses,
        "UFEP-VAL-02": sorted(set(state_problems)),
        "UFEP-VAL-03": sorted(set(unratified)),
        "UFEP-VAL-04": sorted(set(unmeasured)),
        "UFEP-VAL-05": sorted(set(undecidable)),
        "UFEP-VAL-06": sorted(set(baseline_problems)),
        "UFEP-VAL-07": sorted(set(incomplete_records)),
        "UFEP-VAL-08": sorted(set(drift_problems)),
        "UFEP-VAL-09": sorted(set(unreachable_states))
        + [f"{entry['id']}: acted upon" for entry in authorizations if entry["acted_on"]],
        "UFEP-VAL-10": sorted(set(unmeasured_criteria)),
        "UFEP-VAL-11": [f"{item}: a valid ratification record is not a declared freeze subject" for item in uncovered],
        "UFEP-VAL-12": sorted(set(unlocated_authorizations)),
        "UFEP-VAL-13": [f"{item}: not eligible" for item in ineligible],
        "UFEP-VAL-14": [f"{item}: unsatisfied" for item in unmet_completion],
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

    freeze_eligibility = bool(subjects) and not ineligible
    constitutional_completion = not unmet_completion and not blocking_failures

    model = {
        "programme": programme,
        "clauses": clauses,
        "states": [
            {
                "state": entry["state"],
                "initial": bool(entry.get("initial")),
                "reachable_by_this_programme": bool(entry.get("reachable_by_this_programme")),
            }
            for entry in document["states"]
        ],
        "transitions": [
            {
                "from": entry["from"],
                "to": entry["to"],
                "requires_freeze_authority": bool(entry.get("requires_freeze_authority")),
            }
            for entry in document["transitions"]
        ],
        "preconditions": [
            {
                "id": entry["id"],
                "precondition": entry["precondition"],
                "scope": entry["scope"],
                "owner": entry["owner"],
            }
            for entry in document["preconditions"]
        ],
        "sources": [evaluations[key] for key in sorted(evaluations)],
        "subjects": subjects,
        "baselines": reproduced,
        "frozen_baselines": manifests,
        "authorizations": authorizations,
        "completion_criteria": completion,
        "validations": validations,
        "counts": {
            "subjects": len(subjects),
            "eligible": sum(1 for item in subjects if item["eligible"]),
            "not_eligible": len(ineligible),
            "preconditions": len(document["preconditions"]),
            "clauses_bound": sum(1 for entry in clauses if entry["bound"]),
            "clauses": len(clauses),
            "frozen_entries": sum(entry["entries"] for entry in manifests),
            "frozen_matched": sum(entry["matched"] for entry in manifests),
            "frozen_drifted": sum(len(entry["drifted"]) for entry in manifests),
            "completion_satisfied": sum(
                1 for entry in completion if entry["outcome"] == SATISFIED
            ),
            "completion_criteria": len(completion),
            "authorizations_located": sum(1 for entry in authorizations if entry["located"]),
        },
        "determination": {
            "freeze_eligibility": freeze_eligibility,
            "constitutional_completion": constitutional_completion,
            "scope": "the artifacts holding a valid canonical record in the located ratification registry",
            "freeze_performed": False,
            "finality": "unchanged — the in-corpus ceiling fixed by the located ratification constitution is preserved",
        },
        "blocking_failures": blocking_failures,
        "gate": gate,
        "gate_exit": 1 if blocking_failures else 0,
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
    determination = model["determination"]
    rows = [
        ["PROGRAMME", f"{programme['id']} — {programme['name']}"],
        ["VERSION", programme["version"]],
        ["AUTHORITY", programme["authority"]],
        ["CLAUSES BOUND", f"{counts['clauses_bound']}/{counts['clauses']}"],
        ["FREEZE SUBJECTS", f"{counts['eligible']}/{counts['subjects']} eligible"],
        ["PRECONDITIONS PER SUBJECT", counts["preconditions"]],
        ["SEALED BASELINE", f"{counts['frozen_matched']}/{counts['frozen_entries']} verified · {counts['frozen_drifted']} drifted"],
        ["COMPLETION CRITERIA", f"{counts['completion_satisfied']}/{counts['completion_criteria']} satisfied"],
        ["FREEZE ELIGIBILITY", "TRUE" if determination["freeze_eligibility"] else "FALSE"],
        ["CONSTITUTIONAL COMPLETION", "TRUE" if determination["constitutional_completion"] else "FALSE"],
        ["FREEZE PERFORMED", "NO — this programme holds no Freeze Authority"],
        ["GATE", model["gate"]],
        ["SEAL (sha256)", model["seal_sha256"]],
        ["GENERATED BY", "ufep_engine.py — regenerated, never hand-authored"],
    ]
    return table(["Field", "Value"], rows) + "\n\n> " + programme["disclosure"]


def render(model: dict) -> dict[str, str]:
    programme = model["programme"]
    determination = model["determination"]
    pages: dict[str, str] = {}

    pages["00-UFEP-DASHBOARD.md"] = "\n".join(
        [
            f"# {programme['id']} — {programme['name']} · Dashboard",
            "",
            front_matter(model),
            "",
            "## Determination",
            "",
            table(
                ["Determination", "Value", "Scope"],
                [
                    [
                        "FREEZE ELIGIBILITY",
                        "**TRUE**" if determination["freeze_eligibility"] else "**FALSE**",
                        determination["scope"],
                    ],
                    [
                        "CONSTITUTIONAL COMPLETION",
                        "**TRUE**" if determination["constitutional_completion"] else "**FALSE**",
                        "every constitutional condition this repository is competent to decide",
                    ],
                    ["FREEZE PERFORMED", "NO", "reserved to Freeze Authority (CEP-007 VII.1, I.5)"],
                    ["CONSTITUTIONAL FINALITY", "UNCHANGED", determination["finality"]],
                ],
            ),
            "",
            "## Freeze states",
            "",
            "Every state past eligibility requires Freeze Authority acting on an authorization.",
            "This programme reaches none of them, and a self-guard fails closed if it ever does.",
            "",
            table(
                ["State", "Initial", "Reachable by this programme"],
                [
                    [
                        f"`{entry['state']}`",
                        "YES" if entry["initial"] else "no",
                        "YES" if entry["reachable_by_this_programme"] else "**NO**",
                    ]
                    for entry in model["states"]
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

    pages["01-FREEZE-ELIGIBILITY-REGISTER.md"] = "\n".join(
        [
            f"# {programme['id']} · Freeze Eligibility Register",
            "",
            "One row per freeze subject. A subject is an artifact holding a valid canonical record",
            "in the located ratification registry — CEP-007 III.2 admits nothing else to the freeze",
            "lifecycle. Eligibility is decided by the five CEP-007 Article V preconditions; where a",
            "subject is not eligible, the unsatisfied precondition is named.",
            "",
            table(
                ["Subject", "Artifact", "Ratification record", "Ratification state", "State", "Eligible", "Unsatisfied"],
                [
                    [
                        f"`{item['id']}`",
                        item["artifact"] or "—",
                        f"`{item['ratification_record']}`",
                        item["ratification_state"] or "—",
                        f"`{item['state']}`",
                        "**YES**" if item["eligible"] else "**NO**",
                        ", ".join(f"`{key}`" for key in item["unsatisfied"]) or "—",
                    ]
                    for item in model["subjects"]
                ],
            ),
            "",
            "## Precondition detail (CEP-007 Article V)",
            "",
            table(
                ["Subject", "Precondition", "Outcome", "Measured from"],
                [
                    [
                        f"`{item['id']}`",
                        f"`{key}`",
                        value["outcome"],
                        f"`{value['owner']}`" if value.get("owner") else "—",
                    ]
                    for item in model["subjects"]
                    for key, value in item["preconditions"].items()
                ],
            ),
            "",
            "## What each precondition is, and who owns it",
            "",
            table(
                ["Precondition", "Requirement", "Scope", "Constitutional owner"],
                [
                    [
                        f"`{entry['id']}`",
                        entry["precondition"],
                        entry["scope"],
                        f"`{entry['owner']}`",
                    ]
                    for entry in model["preconditions"]
                ],
            ),
            "",
        ]
    )

    pages["02-BASELINE-AND-DRIFT-REGISTER.md"] = "\n".join(
        [
            f"# {programme['id']} · Baseline and No-Drift Register",
            "",
            "## The baseline a freeze would seal (CEP-007 Article VIII)",
            "",
            "Content-addressed and computed as a pure function of the ratified act, its bound",
            "evidence digests and its ratification record. Computing a baseline is not sealing one:",
            "nothing here is recorded frozen, and the version is the baseline's own digest so it",
            "cannot drift from the material it summarises.",
            "",
            table(
                ["Subject", "State", "Version", "Baseline digest", "Lineage"],
                [
                    [
                        f"`{item['id']}`",
                        f"`{item['state']}`",
                        item["freeze_record"]["version"],
                        item["freeze_record"]["baseline_digest"][:32],
                        item["freeze_record"]["lineage"] or "— (no predecessor)",
                    ]
                    for item in model["subjects"]
                ],
            ),
            "",
            "## No-drift guard over the located frozen baseline (CEP-007 Article X)",
            "",
            table(
                ["Manifest", "Entries", "Verified", "Drifted", "Missing", "Notice located"],
                [
                    [
                        f"`{entry['manifest']}`",
                        entry["entries"],
                        entry["matched"],
                        len(entry["drifted"]),
                        len(entry["missing"]),
                        "YES" if entry["notice_located"] else "**NO**",
                    ]
                    for entry in model["frozen_baselines"]
                ],
            ),
            "",
            "## Freeze authorization (recorded, not acted upon)",
            "",
            table(
                ["Authorization", "Instrument", "Located", "Acted upon here"],
                [
                    [
                        f"`{entry['id']}`",
                        f"`{entry['owner']}`",
                        "YES" if entry["located"] else "**NO**",
                        "**YES**" if entry["acted_on"] else "NO",
                    ]
                    for entry in model["authorizations"]
                ],
            ),
            "",
        ]
    )

    pages["03-CONSTITUTIONAL-COMPLETION-DETERMINATION.md"] = "\n".join(
        [
            f"# {programme['id']} · Constitutional Completion Determination",
            "",
            front_matter(model),
            "",
            "## Completion criteria",
            "",
            "Each criterion is measured against the sealed machine model of the programme that owns",
            "the condition. Nothing here is asserted; an unreadable source is unsatisfied.",
            "",
            table(
                ["Criterion", "Statement", "Owner model", "Observed", "Outcome"],
                [
                    [
                        f"`{entry['id']}`",
                        entry["criterion"],
                        f"`{entry['owner']}`" if entry.get("owner") else "—",
                        entry.get("observed", "—"),
                        entry["outcome"],
                    ]
                    for entry in model["completion_criteria"]
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
            "## What this determination does and does not mean",
            "",
            "CONSTITUTIONAL COMPLETION here means: every constitutional condition this repository is",
            "competent to decide is decided, measured, owned by a located programme, and enforced by",
            "a gate whose verdict is reachable in both directions. It does NOT mean constitutional",
            "finality, which the located ratification constitution reserves to an authority outside",
            "the corpus, and which no act inside the repository can supply.",
            "",
            "FREEZE ELIGIBILITY here means: for every artifact holding a valid canonical ratification",
            "record, all five CEP-007 Article V preconditions are satisfied, so CEP-007 Article IV",
            "decides the artifact eligible. It does NOT mean a freeze has occurred, has been",
            "authorised by this programme, or is asserted at band or programme scope.",
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
    for key in CLAUSE_KEYS:
        binding = document[key]
        if not (REPO / binding["owner"]).is_file():
            problems.append(f"{key}: owner does not resolve")
        elif not anchor_located(binding):
            problems.append(f"{key}: anchor absent in {binding['owner']}")
    for entry in document["subjects"]:
        for key in ("validation_evidence", "certification_evidence"):
            if not (REPO / entry[key]["owner"]).is_file():
                problems.append(f"{entry['id']}: {key} owner does not resolve")
            elif not anchor_located(entry[key]):
                problems.append(f"{entry['id']}: {key} anchor absent")
    for entry in document["sources"]:
        if not (REPO / entry["owner"]).is_file():
            problems.append(f"{entry['id']}: source does not resolve")
        if entry.get("operator") and entry["operator"] not in OPERATORS:
            problems.append(f"{entry['id']}: unknown operator {entry['operator']!r}")
    for entry in document["frozen_baselines"]:
        for key in ("manifest", "notice"):
            if not (REPO / entry[key]).is_file():
                problems.append(f"{entry['id']}: {key} does not resolve")
    known = {entry["id"] for entry in document["sources"]}
    for entry in document["completion_criteria"]:
        if entry["source"] not in known:
            problems.append(f"{entry['id']}: names an undeclared source")
    seen: set[str] = set()
    for section in ("states", "preconditions", "sources", "subjects", "frozen_baselines", "authorizations", "completion_criteria", "validations", "exit_criteria"):
        for entry in document[section]:
            identifier = entry.get("id")
            if identifier in seen:
                problems.append(f"{section}: duplicate id {identifier}")
            if identifier:
                seen.add(identifier)
    return problems


def check_no_enumeration(document: dict) -> list[str]:
    """No freeze state, subject identifier or located act may be a literal in this engine."""
    source = Path(__file__).read_text(encoding="utf-8")
    leaked: list[str] = []
    for entry in document["states"]:
        if entry["state"] in source:
            leaked.append(f"state {entry['state']}")
    for entry in document["subjects"]:
        if entry["id"] in source:
            leaked.append(f"subject {entry['id']}")
        for key in ("validation_evidence", "certification_evidence"):
            if entry[key]["owner"] in source:
                leaked.append(f"evidence path {entry[key]['owner']}")
    for entry in document["frozen_baselines"]:
        if entry["manifest"] in source:
            leaked.append(f"manifest {entry['manifest']}")
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
    problems = sorted(name for name in first if first[name] != second.get(name))
    left, right = measure(document)["baselines"], measure(document)["baselines"]
    problems.extend(
        f"baseline not reproducible: {key}" for key in sorted(left) if left[key] != right.get(key)
    )
    return problems


def check_no_freeze(document: dict) -> list[str]:
    """No subject may occupy a state this programme cannot reach; no authorization may be acted on."""
    model = measure(document)
    reachable = {
        entry["state"] for entry in model["states"] if entry["reachable_by_this_programme"]
    }
    problems = [
        f"{item['id']}: reported in {item['state']}"
        for item in model["subjects"]
        if item["state"] not in reachable
    ]
    problems += [
        f"{entry['id']}: acted upon by this programme"
        for entry in model["authorizations"]
        if entry["acted_on"]
    ]
    if model["determination"]["freeze_performed"]:
        problems.append("the determination claims a freeze was performed")
    return problems


def check_no_drift(document: dict) -> list[str]:
    model = measure(document)
    problems: list[str] = []
    for entry in model["frozen_baselines"]:
        if not entry["readable"]:
            problems.append(f"{entry['id']}: manifest does not resolve")
            continue
        problems.extend(f"{entry['id']}: drifted {path}" for path in entry["drifted"])
        problems.extend(f"{entry['id']}: missing {path}" for path in entry["missing"])
        if entry["matched"] != entry["entries"]:
            problems.append(f"{entry['id']}: {entry['matched']} of {entry['entries']} verified")
    return problems


GUARDS = {
    "check-declaration": check_declaration,
    "check-no-enumeration": check_no_enumeration,
    "check-write-scope": check_write_scope,
    "check-determinism": check_determinism,
    "check-no-freeze": check_no_freeze,
    "check-no-drift": check_no_drift,
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
        print(f"UCOS-UFEP-001 ABORT: {exc}", file=sys.stderr)
        return 2

    selected = [name for name in GUARDS if getattr(args, name.replace("-", "_"))]
    if selected:
        failed = False
        for name in selected:
            try:
                problems = GUARDS[name](document)
            except FailClosed as exc:
                print(f"UCOS-UFEP-001 ABORT: {exc}", file=sys.stderr)
                return 2
            if problems:
                failed = True
                print(f"UCOS-UFEP-001 {name}: FAIL ({len(problems)})", file=sys.stderr)
                for problem in problems[:40]:
                    print(f"  - {problem}", file=sys.stderr)
            else:
                print(f"UCOS-UFEP-001 {name}: PASS")
        return 1 if failed else 0

    try:
        model = measure(document)
    except FailClosed as exc:
        print(f"UCOS-UFEP-001 ABORT: {exc}", file=sys.stderr)
        return 2

    written = write_registers(model)
    counts = model["counts"]
    determination = model["determination"]
    if not args.quiet:
        print(
            f"UCOS-UFEP-001: FREEZE-ELIGIBILITY={'TRUE' if determination['freeze_eligibility'] else 'FALSE'} "
            f"CONSTITUTIONAL-COMPLETION={'TRUE' if determination['constitutional_completion'] else 'FALSE'} "
            f"| subjects={counts['eligible']}/{counts['subjects']} eligible "
            f"| completion={counts['completion_satisfied']}/{counts['completion_criteria']} "
            f"| frozen-baseline={counts['frozen_matched']}/{counts['frozen_entries']} verified "
            f"| drifted={counts['frozen_drifted']} | freeze-performed=NO "
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
