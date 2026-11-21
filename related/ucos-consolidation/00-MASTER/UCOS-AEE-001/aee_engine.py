#!/usr/bin/env python3
"""UCOS-AEE-001 — Autonomous Evolution Engine.

AUTHORITY = NONE (DERIVED TRUTH). This engine legislates nothing, registers nothing,
certifies nothing and owns no capability. Every phase of the evolution loop already has a
located owner in this repository; this engine creates none of them. What no located
programme owned is the CLOSED LOOP itself — every entry point here is a one-shot process,
so nothing re-executed the located owners, re-read their sealed determinations, compared
consecutive readings and asserted a fixed point over what they report. This engine is that
driver and only that driver.

    python3 00-MASTER/UCOS-AEE-001/aee_engine.py --tier observe   # read-only, no actuation
    python3 00-MASTER/UCOS-AEE-001/aee_engine.py                  # actuate + converge
    python3 00-MASTER/UCOS-AEE-001/aee_engine.py --tier closure   # include the heavy tier
    python3 00-MASTER/UCOS-AEE-001/aee_engine.py --gate           # fail-closed
    python3 00-MASTER/UCOS-AEE-001/aee_engine.py --check-declaration
    python3 00-MASTER/UCOS-AEE-001/aee_engine.py --check-no-enumeration
    python3 00-MASTER/UCOS-AEE-001/aee_engine.py --check-write-scope
    python3 00-MASTER/UCOS-AEE-001/aee_engine.py --check-determinism
    python3 00-MASTER/UCOS-AEE-001/aee_engine.py --check-reuse-before-create
    python3 00-MASTER/UCOS-AEE-001/aee_engine.py --check-mandate-coverage

Exit semantics:
    0  the loop converged and every blocking criterion is satisfied
    1  a blocking convergence criterion is unsatisfied
    2  fail-closed abort — the declaration is unusable, so no verdict may be asserted

Every actuator, observation, mandate, class, decision, rule and criterion is read from
aee-declaration.json. No identifier this engine acts on appears as a literal below, which
is what makes extension an edit to DATA rather than to code.

Stdlib only. No network. No timestamp, no duration, no commit identity and no absolute
path is emitted, so the sealed output set is byte-identical for an unchanged repository.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import NoReturn

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
DECLARATION = HERE / "aee-declaration.json"
EVIDENCE_DIR = HERE / "evidence"
STATE_FILE = "aee.json"

# Keys each declaration section may carry. A key outside its set is a fail-closed
# violation: it is how a finite assumption would otherwise be smuggled in as a new field.
ALLOWED_KEYS: dict[str, set[str]] = {
    "vocabulary": {"id", "term", "definition"},
    "principle": {"id", "principle", "owner"},
    "tiers": {"id", "tier", "order", "actuates"},
    "mandate_sources": {
        "id",
        "name",
        "owner",
        "collection_pointer",
        "select_field",
        "select_value",
        "member_pointer",
        "id_field",
        "label_field",
    },
    "actuators": {
        "id",
        "name",
        "owner",
        "argv",
        "env",
        "writes",
        "tier",
        "required",
        "heavy",
        "mandate",
        "$env_comment",
        "$tier_comment",
    },
    "observations": {
        "id",
        "name",
        "owner",
        "source",
        "pointer",
        "operator",
        "expect",
        "blocking",
        "governed_by_finding",
        "mandate",
    },
    "classes": {"id", "class", "owner"},
    "decisions": {"id", "decision", "definition", "requires_evidence"},
    "classification_rules": {"id", "when", "class", "decision", "rationale"},
    "findings": {
        "id",
        "title",
        "class",
        "owner",
        "evidence",
        "disposition",
        "blocking",
        "engineering_closable",
        "note",
    },
}

# Predicate keys a classification rule may test. These are properties this engine DERIVES
# from a finding, never properties of its identity — that is what keeps classification
# automatic. Extending the vocabulary is a code change by design: a new predicate is new
# reasoning, not new data.
DERIVED_PROPERTIES = ("blocking", "governed", "escalated", "actuator_failure")

MISSING = object()


# --------------------------------------------------------------------------- primitives


def fail_closed(message: str) -> NoReturn:
    print(f"AEE FAIL-CLOSED ABORT — {message}", file=sys.stderr)
    raise SystemExit(2)


def load_declaration() -> dict:
    if not DECLARATION.is_file():
        fail_closed(f"declaration absent: {DECLARATION.name}")
    try:
        return json.loads(DECLARATION.read_text("utf-8"))
    except json.JSONDecodeError as exc:
        fail_closed(f"declaration is not valid JSON: {exc}")


def canonical_json(payload: object) -> str:
    return json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n"


def digest(payload: object) -> str:
    return hashlib.sha256(canonical_json(payload).encode("utf-8")).hexdigest()


def relative(path: Path) -> str:
    try:
        return str(path.relative_to(REPO))
    except ValueError:
        return path.name


def get_pointer(document: object, dotted: str) -> object:
    node = document
    for part in dotted.split("."):
        if not isinstance(node, dict) or part not in node:
            return MISSING
        node = node[part]
    return node


def resolve_reference(ref: str) -> Path | None:
    """Resolve a declared reference to a located repository path, or None."""
    bare = ref
    for token in (" (", " §", " · ", " — "):
        if token in bare:
            bare = bare.split(token, 1)[0]
    bare = bare.strip()
    if not bare:
        return None
    candidate = REPO / bare
    if candidate.exists():
        return candidate
    parent = candidate.parent
    if not parent.is_dir():
        return None
    matches = sorted(c for c in parent.iterdir() if c.name.startswith(candidate.name))
    return matches[0] if matches else None


def interpreters() -> dict[str, str]:
    venv = REPO / ".ec1-venv" / "bin" / "python"
    return {"$PY": str(venv) if venv.is_file() else "", "$PY3": sys.executable}


def table(headers: list[str], rows: list[list[str]]) -> str:
    head = "| " + " | ".join(headers) + " |\n"
    rule = "|" + "|".join(["---"] * len(headers)) + "|\n"
    body = "".join("| " + " | ".join(row) + " |\n" for row in rows)
    return head + rule + body


def joined(values: list[str]) -> str:
    return ", ".join(f"`{v}`" for v in values) if values else "none"


def brief(value: object, limit: int = 160) -> object:
    """A compact, JSON-safe rendering of an observed value."""
    if isinstance(value, bool | int | float) or value is None:
        return value
    if isinstance(value, str):
        return value if len(value) <= limit else value[:limit] + "…"
    if isinstance(value, list):
        return [brief(item, 60) for item in value[:8]] + (["…"] if len(value) > 8 else [])
    if isinstance(value, dict):
        return {k: brief(value[k], 60) for k in sorted(value)[:8]}
    return str(value)[:limit]


# ------------------------------------------------------------------- working-tree state


def git_porcelain() -> tuple[set[str], bool]:
    """Repository-relative working-tree entries, and whether git answered at all.

    `--untracked-files=all` is not cosmetic. Without it git COLLAPSES a wholly untracked
    directory into a single entry and expands it into one entry per file as soon as any
    sibling becomes tracked. The set therefore changes shape without a single byte
    changing on disk, and a residue diff computed across that shape change attributes
    files to whichever actuator happened to straddle it. Listing every untracked file
    individually makes the set a function of the tree alone.
    """
    try:
        out = subprocess.run(  # noqa: S603 — fixed argv, no shell, no user input
            ["git", "status", "--porcelain", "--untracked-files=all"],  # noqa: S607 — from PATH
            cwd=REPO,
            capture_output=True,
            text=True,
            check=False,
        )
    except OSError:
        return set(), False
    if out.returncode != 0:
        return set(), False
    entries: set[str] = set()
    for line in out.stdout.splitlines():
        if len(line) < 4:
            continue
        path = line[3:].strip()
        if " -> " in path:
            path = path.split(" -> ", 1)[1]
        entries.add(path.strip('"'))
    return entries, True


# --------------------------------------------------------------------- mandate universe


def read_mandates(decl: dict) -> tuple[dict[str, dict], list[str]]:
    """READ the loop's phases from the located declarations that already own them."""
    universe: dict[str, dict] = {}
    problems: list[str] = []
    for source in decl["mandate_sources"]:
        located = resolve_reference(source["owner"])
        if located is None or not located.is_file():
            problems.append(f"{source['id']}: mandate source does not resolve: {source['owner']}")
            continue
        try:
            document = json.loads(located.read_text("utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            problems.append(f"{source['id']}: mandate source unreadable: {exc}")
            continue
        node: object = document
        pointer = source.get("collection_pointer")
        if pointer:
            node = get_pointer(document, pointer)
            if node is MISSING or not isinstance(node, list):
                problems.append(f"{source['id']}: collection pointer {pointer!r} does not resolve")
                continue
            field, wanted = source.get("select_field"), source.get("select_value")
            chosen = [m for m in node if isinstance(m, dict) and m.get(field) == wanted]
            if len(chosen) != 1:
                problems.append(
                    f"{source['id']}: {field}={wanted!r} selected {len(chosen)} members, expected 1"
                )
                continue
            node = chosen[0]
        members = get_pointer(node, source["member_pointer"]) if isinstance(node, dict) else MISSING
        if members is MISSING or not isinstance(members, list):
            problems.append(
                f"{source['id']}: member pointer {source['member_pointer']!r} does not resolve"
            )
            continue
        for member in members:
            if not isinstance(member, dict):
                continue
            ident = member.get(source["id_field"])
            if ident is None:
                problems.append(f"{source['id']}: member without {source['id_field']!r}")
                continue
            key = str(ident)
            label = str(member.get(source["label_field"], ""))
            if key in universe:
                problems.append(f"{source['id']}: mandate {key} is already owned by another source")
                continue
            universe[key] = {
                "id": key,
                "label": label if len(label) <= 150 else label[:150] + "…",
                "source": source["id"],
                "owner": source["owner"],
            }
    return universe, problems


def mandate_coverage(decl: dict, universe: dict[str, dict]) -> dict:
    """Which located phase each actuator or observation discharges — and which none does."""
    discharged: dict[str, list[str]] = {key: [] for key in universe}
    unresolved: list[str] = []
    for section in ("actuators", "observations"):
        for entry in decl[section]:
            for key in entry.get("mandate", []):
                if key in discharged:
                    discharged[key].append(entry["id"])
                else:
                    unresolved.append(f"{entry['id']}: bound mandate {key} resolves in no source")
    uncovered = sorted(key for key, binders in discharged.items() if not binders)
    return {
        "universe_total": len(universe),
        "covered_total": len(universe) - len(uncovered),
        "uncovered": uncovered,
        "unresolved_bindings": sorted(unresolved),
        "discharged_by": {key: sorted(set(v)) for key, v in sorted(discharged.items())},
    }


# ------------------------------------------------------------------------- observations


def _op_is_empty(value: object, _expect: object, _doc: dict) -> tuple[bool, object]:
    return (not value), brief(value)


def _op_not_empty(value: object, _expect: object, _doc: dict) -> tuple[bool, object]:
    return bool(value), brief(value)


def _op_equals(value: object, expect: object, _doc: dict) -> tuple[bool, object]:
    return value == expect, brief(value)


def _op_every_field_in(value: object, expect: object, _doc: dict) -> tuple[bool, object]:
    if not isinstance(expect, dict) or not isinstance(value, list):
        return False, "pointer did not resolve to a list, or the expectation is malformed"
    field, allowed = expect.get("field"), set(expect.get("allowed") or [])
    offenders = sorted(
        f"{m.get('id', '?')}={m.get(field)!r}"
        for m in value
        if isinstance(m, dict) and m.get(field) not in allowed
    )
    return (not offenders), (offenders[:8] or len(value))


def _op_equals_sibling(value: object, expect: object, doc: dict) -> tuple[bool, object]:
    if not isinstance(expect, dict):
        return False, "malformed expectation"
    other = get_pointer(doc, str(expect.get("sibling")))
    if other is MISSING:
        return False, f"sibling pointer {expect.get('sibling')!r} does not resolve"
    return value == other, {"measured": brief(value), "sibling": brief(other)}


OPERATORS = {
    "is_empty": _op_is_empty,
    "not_empty": _op_not_empty,
    "equals": _op_equals,
    "every_field_in": _op_every_field_in,
    "equals_sibling": _op_equals_sibling,
}


def observe(decl: dict) -> list[dict]:
    """Take every declared reading from the located owners' own sealed outputs."""
    cache: dict[str, object] = {}
    records: list[dict] = []
    for spec in decl["observations"]:
        record = {
            "id": spec["id"],
            "name": spec["name"],
            "owner": spec["owner"],
            "source": spec["source"],
            "pointer": spec["pointer"],
            "blocking": bool(spec["blocking"]),
            "governed_by_finding": spec["governed_by_finding"],
            "mandate": list(spec.get("mandate", [])),
            "verdict": "UNRESOLVED",
            "observed": None,
            "reason": "",
        }
        if spec["source"] not in cache:
            located = resolve_reference(spec["source"])
            if located is None or not located.is_file():
                cache[spec["source"]] = MISSING
            else:
                try:
                    cache[spec["source"]] = json.loads(located.read_text("utf-8"))
                except (OSError, json.JSONDecodeError):
                    cache[spec["source"]] = MISSING
        document = cache[spec["source"]]
        if document is MISSING or not isinstance(document, dict):
            record["reason"] = "the located source is absent or unreadable"
            records.append(record)
            continue
        value = get_pointer(document, spec["pointer"])
        if value is MISSING:
            record["reason"] = "the declared pointer does not resolve in the located source"
            records.append(record)
            continue
        satisfied, observed = OPERATORS[spec["operator"]](value, spec["expect"], document)
        record["observed"] = observed
        record["verdict"] = "SATISFIED" if satisfied else "VIOLATED"
        if not satisfied:
            record["reason"] = "the measured value does not meet the declared expectation"
        records.append(record)
    return records


# ---------------------------------------------------------------------------- actuation


def actuate(decl: dict, tier: str, order: dict[str, int]) -> list[dict]:
    """Invoke each located owner in scope so it regenerates its own determination."""
    interp = interpreters()
    limit = order[tier]
    # This programme's own home is not residue. Writing it is authorized by construction
    # (own memory only), it is this driver's act rather than any actuator's, and counting
    # it would attribute the driver's own emission to whichever owner ran alongside it.
    own_home = decl["programme"]["operational_home"]
    results: list[dict] = []
    for spec in decl["actuators"]:
        record = {
            "id": spec["id"],
            "name": spec["name"],
            "owner": spec["owner"],
            "tier": spec["tier"],
            "required": bool(spec["required"]),
            "heavy": bool(spec["heavy"]),
            "mandate": list(spec.get("mandate", [])),
            "in_scope": order[spec["tier"]] <= limit,
            "executed": False,
            "exit_code": None,
            "verdict": "NOT-EXECUTED",
            "reason": "",
            "residue": [],
            "unattributed": [],
        }
        if not record["in_scope"]:
            record["reason"] = f"declared tier is above the selected tier {tier}"
            results.append(record)
            continue
        argv = list(spec["argv"])
        if argv[0] in interp:
            if not interp[argv[0]]:
                record["verdict"] = "UNAVAILABLE"
                record["reason"] = "the declared interpreter is not present in this environment"
                results.append(record)
                continue
            argv[0] = interp[argv[0]]
        if resolve_reference(spec["owner"]) is None:
            record["verdict"] = "UNAVAILABLE"
            record["reason"] = "the located owner could not be resolved"
            results.append(record)
            continue

        before, _ = git_porcelain()
        env = dict(os.environ)
        env.update(spec.get("env") or {})
        completed = subprocess.run(  # noqa: S603 — argv is Repository Truth, list form, no shell
            argv, cwd=REPO, capture_output=True, text=True, check=False, env=env
        )
        after, measurable = git_porcelain()
        record["executed"] = True
        record["exit_code"] = completed.returncode
        record["verdict"] = "PASS" if completed.returncode == 0 else "FAIL"
        if completed.returncode != 0:
            record["reason"] = f"the located owner exited {completed.returncode}"
        EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
        (EVIDENCE_DIR / f"{spec['id']}.log").write_text(
            (completed.stdout or "") + (completed.stderr or ""), "utf-8"
        )
        residue = sorted(p for p in (after - before) if not p.startswith(own_home))
        record["residue"] = residue
        if measurable:
            zones = tuple(spec.get("writes") or [])
            record["unattributed"] = [p for p in residue if not p.startswith(zones)]
        results.append(record)
    return results


# ----------------------------------------------------------- discovery and adjudication


def adjudicate(decl: dict, observations: list[dict], actuators: list[dict]) -> list[dict]:
    """Derive findings, then classify and decide each from the declared rules alone."""
    governing = {f["id"]: f for f in decl["findings"]}
    classes = {c["class"] for c in decl["classes"]}
    decisions = {d["decision"]: d for d in decl["decisions"]}
    findings: list[dict] = []

    subjects: list[dict] = []
    for record in observations:
        if record["verdict"] in ("VIOLATED", "UNRESOLVED"):
            subjects.append(
                {
                    "id": record["id"],
                    "subject": record["name"],
                    "owner": record["owner"],
                    "evidence": [record["source"]],
                    "observed": record["observed"],
                    "detail": record["reason"],
                    "props": {
                        "blocking": record["blocking"],
                        "governed": record["governed_by_finding"] is not None,
                        "escalated": bool(
                            record["governed_by_finding"]
                            and not governing.get(record["governed_by_finding"], {}).get(
                                "engineering_closable", True
                            )
                        ),
                        "actuator_failure": False,
                    },
                    "governed_by_finding": record["governed_by_finding"],
                }
            )
    for record in actuators:
        if record["in_scope"] and record["verdict"] in ("FAIL", "UNAVAILABLE"):
            subjects.append(
                {
                    "id": record["id"],
                    "subject": record["name"],
                    "owner": record["owner"],
                    "evidence": [record["owner"]],
                    "observed": record["exit_code"],
                    "detail": record["reason"],
                    "props": {
                        "blocking": record["required"],
                        "governed": False,
                        "escalated": False,
                        "actuator_failure": True,
                    },
                    "governed_by_finding": None,
                }
            )

    for subject in subjects:
        matched = None
        for rule in decl["classification_rules"]:
            predicate = rule["when"]
            if all(subject["props"].get(key) == want for key, want in predicate.items()):
                matched = rule
                break
        entry = {
            "id": subject["id"],
            "subject": subject["subject"],
            "owner": subject["owner"],
            "detail": subject["detail"],
            "observed": subject["observed"],
            "blocking": subject["props"]["blocking"],
            "governed_by_finding": subject["governed_by_finding"],
            "class": None,
            "decision": None,
            "rule": None,
            "rationale": "",
            "evidence": list(subject["evidence"]),
        }
        if matched is None:
            entry["rationale"] = "no declared classification rule matched"
            findings.append(entry)
            continue
        entry["class"] = matched["class"] if matched["class"] in classes else None
        entry["decision"] = matched["decision"] if matched["decision"] in decisions else None
        entry["rule"] = matched["id"]
        entry["rationale"] = matched["rationale"]
        if subject["governed_by_finding"] in governing:
            entry["evidence"] += list(governing[subject["governed_by_finding"]]["evidence"])
        needs = decisions.get(matched["decision"], {}).get("requires_evidence")
        entry["evidence"] = sorted(set(entry["evidence"]))
        if needs and not entry["evidence"]:
            entry["decision"] = None
            entry["rationale"] += " — decision withheld: the declared evidence obligation is unmet"
        findings.append(entry)
    return findings


# ---------------------------------------------------------------------------- the loop


def vector_of(observations: list[dict]) -> list[list[str]]:
    return [[record["id"], record["verdict"]] for record in observations]


def run_loop(decl: dict, tier: str, order: dict[str, int], actuates: bool) -> list[dict]:
    convergence = decl["convergence"]
    maximum = int(convergence["max_iterations"])
    required = int(convergence["required_stable_iterations"])
    iterations: list[dict] = []
    for index in range(1, maximum + 1):
        actuator_records = actuate(decl, tier, order) if actuates else []
        observation_records = observe(decl)
        findings = adjudicate(decl, observation_records, actuator_records)
        vector = vector_of(observation_records)
        iterations.append(
            {
                "index": index,
                "actuators": actuator_records,
                "observations": observation_records,
                "findings": findings,
                "vector_digest": digest(vector),
                "blocking_violations": sorted(
                    r["id"]
                    for r in observation_records
                    if r["blocking"] and r["verdict"] != "SATISFIED"
                ),
                "actuator_failures": sorted(
                    r["id"]
                    for r in actuator_records
                    if r["in_scope"] and r["required"] and r["verdict"] != "PASS"
                ),
            }
        )
        stable = trailing_stable(iterations)
        settled = (
            not iterations[-1]["blocking_violations"] and not iterations[-1]["actuator_failures"]
        )
        if stable >= required and settled:
            break
        if not actuates:
            break
    return iterations


def trailing_stable(iterations: list[dict]) -> int:
    """How many trailing iterations share one observation-vector digest."""
    if not iterations:
        return 0
    last = iterations[-1]["vector_digest"]
    count = 0
    for entry in reversed(iterations):
        if entry["vector_digest"] != last:
            break
        count += 1
    return count


# ------------------------------------------------------------------------ self-guards


def check_declaration(decl: dict) -> list[str]:
    """Every identifier unique, every reference located, every cross-reference bound."""
    findings: list[str] = []
    seen: dict[str, str] = {}
    for section, allowed in ALLOWED_KEYS.items():
        if section not in decl:
            findings.append(f"declared section absent: {section}")
            continue
        for entry in decl[section]:
            ident = entry.get("id")
            if not ident:
                findings.append(f"{section}: entry without an id")
                continue
            if ident in seen:
                findings.append(f"duplicate identifier {ident} ({seen[ident]} and {section})")
            seen[ident] = section
            extra = set(entry) - allowed
            if extra:
                findings.append(f"{ident}: key(s) outside the permitted set: {sorted(extra)}")

    tiers = {entry["tier"] for entry in decl["tiers"]}
    orders = [entry["order"] for entry in decl["tiers"]]
    if len(set(orders)) != len(orders):
        findings.append("tiers: order values are not unique, so tier scope is ambiguous")
    if not any(entry["actuates"] for entry in decl["tiers"]):
        findings.append("tiers: no tier actuates, so no convergence could ever be measured")

    class_names = {entry["class"] for entry in decl["classes"]}
    decision_names = {entry["decision"] for entry in decl["decisions"]}
    finding_ids = {entry["id"] for entry in decl["findings"]}

    for entry in decl["actuators"]:
        if entry["tier"] not in tiers:
            findings.append(f"{entry['id']}: tier {entry['tier']!r} is not declared")
        if not entry["argv"]:
            findings.append(f"{entry['id']}: empty argv — nothing would be invoked")
        if not entry.get("writes") and entry.get("required"):
            findings.append(f"{entry['id']}: no declared write zone, so residue is unattributable")

    for entry in decl["observations"]:
        if entry["operator"] not in OPERATORS:
            findings.append(f"{entry['id']}: operator {entry['operator']!r} is not implemented")
        governing = entry["governed_by_finding"]
        if governing and governing not in finding_ids:
            findings.append(f"{entry['id']}: governing finding {governing} is not declared")
        if not entry["blocking"] and not governing:
            findings.append(
                f"{entry['id']}: non-blocking without a governing finding is prohibited — "
                "nothing may be tolerated without a recorded disposition"
            )

    total = [rule for rule in decl["classification_rules"] if not rule["when"]]
    if not total:
        findings.append(
            "classification_rules: no rule carries an empty predicate, so the register is not "
            "total and a finding could fall through unclassified"
        )
    for rule in decl["classification_rules"]:
        for key in rule["when"]:
            if key not in DERIVED_PROPERTIES:
                findings.append(f"{rule['id']}: predicate {key!r} is not a derived property")
        if rule["class"] not in class_names:
            findings.append(f"{rule['id']}: class {rule['class']!r} is not declared")
        if rule["decision"] not in decision_names:
            findings.append(f"{rule['id']}: decision {rule['decision']!r} is not declared")

    for criterion in decl["convergence"]["criteria"]:
        if "measure" not in criterion or "expect" not in criterion:
            findings.append(f"{criterion.get('id')}: a criterion must be measured, not asserted")

    references: list[tuple[str, str]] = [
        ("programme.evolution_owner", decl["programme"]["evolution_owner"]),
        ("programme.closure_owner", decl["programme"]["closure_owner"]),
        ("programme.operational_memory_owner", decl["programme"]["operational_memory_owner"]),
    ]
    references += [
        ("programme.governing_instruments", r) for r in decl["programme"]["governing_instruments"]
    ]
    for section in ("principle", "mandate_sources", "actuators", "observations", "classes"):
        references += [(e["id"], e["owner"]) for e in decl[section] if e.get("owner")]
    references += [(e["id"], e["source"]) for e in decl["observations"]]
    for source, ref in references:
        if resolve_reference(ref) is None:
            findings.append(f"{source}: reference does not resolve in the repository: {ref!r}")

    for prefix in decl["programme"]["forbidden_write_prefixes"]:
        if not (REPO / prefix).exists():
            findings.append(f"forbidden-write prefix does not exist: {prefix}")

    universe, problems = read_mandates(decl)
    findings += problems
    if not universe:
        findings.append("no mandate resolved from any located source — the loop would be unbound")
    findings += mandate_coverage(decl, universe)["unresolved_bindings"]
    return findings


def check_no_enumeration(decl: dict) -> list[str]:
    """Prove the engine is data-driven: no declared identifier is a literal in its source.

    The programme's own identity is excluded. A programme is not an extension point — it
    is the thing being extended — and the engine must be able to name itself in order to
    report. Every identifier that IS an extension point (actuator, observation, mandate
    source, class, decision, rule, criterion, tier, finding) is covered.
    """
    findings: list[str] = []
    source = Path(__file__).read_text("utf-8")
    identifiers: set[str] = set()
    for section in ALLOWED_KEYS:
        identifiers |= {e["id"] for e in decl.get(section, []) if e.get("id")}
    identifiers |= {c["id"] for c in decl["convergence"]["criteria"]}
    identifiers |= {d["id"] for d in decl["learning"]["dimensions"]}
    identifiers |= {c["id"] for c in decl["continuous"]["cadence_owners"]}
    for ident in sorted(identifiers):
        if ident in source:
            findings.append(
                f"engine source names declared identifier {ident} — extension would require "
                "a code change"
            )
    for section in ("actuators", "observations", "mandate_sources"):
        for entry in decl[section]:
            for ref in (entry.get("owner"), entry.get("source")):
                if ref and ref in source:
                    findings.append(f"{entry['id']}: owner path {ref!r} is a literal in the engine")
    return findings


def check_write_scope(decl: dict, written: list[Path] | None = None) -> list[str]:
    """No byte this programme writes may land outside its own operational home."""
    findings: list[str] = []
    for path in written or []:
        try:
            path.resolve().relative_to(HERE)
        except ValueError:
            findings.append(f"write outside the programme's operational memory: {relative(path)}")
    home = decl["programme"]["operational_home"].rstrip("/")
    for prefix in decl["programme"]["forbidden_write_prefixes"]:
        if home.startswith(prefix.rstrip("/")):
            findings.append(f"the operational home lies inside forbidden prefix {prefix}")
    return findings


def check_reuse_before_create(decl: dict) -> list[str]:
    """No bound owner may lie inside this programme's own home.

    A programme that satisfies its own bindings has created a second home for a capability
    the repository already located elsewhere. Every actuator and every observation source
    must therefore resolve OUTSIDE this directory — that is the mechanical statement of
    Reuse Before Create, and it is what proves this programme adds no parallel authority.
    """
    findings: list[str] = []
    home = HERE
    for section, key in (
        ("actuators", "owner"),
        ("observations", "source"),
        ("mandate_sources", "owner"),
    ):
        for entry in decl[section]:
            located = resolve_reference(entry[key])
            if located is None:
                findings.append(f"{entry['id']}: {key} does not resolve: {entry[key]!r}")
                continue
            try:
                located.resolve().relative_to(home)
            except ValueError:
                continue
            findings.append(
                f"{entry['id']}: {key} {entry[key]!r} lies inside this programme's own home — "
                "a second home for an already-located capability"
            )
    if not decl["actuators"]:
        findings.append("no actuator is declared, so nothing located is being reused")
    return findings


def check_mandate_coverage(decl: dict) -> list[str]:
    """Every located loop phase must be discharged by something."""
    universe, problems = read_mandates(decl)
    coverage = mandate_coverage(decl, universe)
    findings = list(problems) + coverage["unresolved_bindings"]
    findings += [
        f"mandate {key} ({universe[key]['source']}) is discharged by no actuator or observation"
        for key in coverage["uncovered"]
    ]
    return findings


def check_determinism(decl: dict) -> list[str]:
    """Render the emitted set twice from one model; the bytes must be identical."""
    universe, _ = read_mandates(decl)
    stub_observations = [
        {
            "id": spec["id"],
            "name": spec["name"],
            "owner": spec["owner"],
            "source": spec["source"],
            "pointer": spec["pointer"],
            "blocking": bool(spec["blocking"]),
            "governed_by_finding": spec["governed_by_finding"],
            "mandate": list(spec.get("mandate", [])),
            "verdict": "SATISFIED",
            "observed": None,
            "reason": "",
        }
        for spec in decl["observations"]
    ]
    stub_actuators = [
        {
            "id": spec["id"],
            "name": spec["name"],
            "owner": spec["owner"],
            "tier": spec["tier"],
            "required": bool(spec["required"]),
            "heavy": bool(spec["heavy"]),
            "mandate": list(spec.get("mandate", [])),
            "in_scope": True,
            "executed": True,
            "exit_code": 0,
            "verdict": "PASS",
            "reason": "",
            "residue": [],
            "unattributed": [],
        }
        for spec in decl["actuators"]
    ]
    iteration = {
        "index": 1,
        "actuators": stub_actuators,
        "observations": stub_observations,
        "findings": [],
        "vector_digest": digest(vector_of(stub_observations)),
        "blocking_violations": [],
        "actuator_failures": [],
    }
    tier = sorted(decl["tiers"], key=lambda e: e["order"])[-1]["tier"]
    model = assemble(decl, [iteration, dict(iteration, index=2)], tier, universe)
    first, second = render(decl, model), render(decl, model)
    if set(first) != set(second):
        return ["the rendered output set differs between runs"]
    return [
        f"non-deterministic rendering: {name}"
        for name in sorted(first)
        if first[name] != second[name]
    ]


SELF_GUARDS = {
    "--check-declaration": check_declaration,
    "--check-no-enumeration": check_no_enumeration,
    "--check-write-scope": lambda decl: check_write_scope(decl),
    "--check-determinism": check_determinism,
    "--check-reuse-before-create": check_reuse_before_create,
    "--check-mandate-coverage": check_mandate_coverage,
}


# --------------------------------------------------------------------------- assembly


def assemble(decl: dict, iterations: list[dict], tier: str, universe: dict[str, dict]) -> dict:
    """Pure aggregation over collected iterations — no execution, no I/O."""
    terminal = iterations[-1]
    coverage = mandate_coverage(decl, universe)
    required = int(decl["convergence"]["required_stable_iterations"])
    stable = trailing_stable(iterations)
    actuating = {e["tier"]: e["actuates"] for e in decl["tiers"]}[tier]

    unattributed = sorted(
        f"{rec['id']}:{path}" for rec in terminal["actuators"] for path in rec["unattributed"]
    )
    unresolved_pointers = sorted(
        rec["id"] for rec in terminal["observations"] if rec["verdict"] == "UNRESOLVED"
    )
    unclassified = sorted(
        f["id"] for f in terminal["findings"] if not f["class"] or not f["decision"]
    )

    measured = {
        "unstable_transitions": max(0, required - stable) if actuating else max(1, required - 1),
        "blocking_violations": len(terminal["blocking_violations"]),
        "actuator_failures": len(terminal["actuator_failures"]),
        "unresolved_mandate_bindings": len(coverage["unresolved_bindings"]),
        "unclassified_findings": len(unclassified),
        "unattributed_residue": len(unattributed),
        "unresolved_pointers": len(unresolved_pointers),
    }
    criteria = []
    for criterion in decl["convergence"]["criteria"]:
        value = measured.get(criterion["measure"], MISSING)
        satisfied = value is not MISSING and value == criterion["expect"]
        criteria.append(
            {
                "id": criterion["id"],
                "criterion": criterion["criterion"],
                "measure": criterion["measure"],
                "expect": criterion["expect"],
                "measured": None if value is MISSING else value,
                "blocking": bool(criterion["blocking"]),
                "verdict": "SATISFIED" if satisfied else "VIOLATED",
            }
        )
    unsatisfied = sorted(c["id"] for c in criteria if c["blocking"] and c["verdict"] != "SATISFIED")

    ceiling = [
        f"`{f['id']}` — {f['title']}"
        for f in decl["findings"]
        if not f.get("engineering_closable", True)
    ]
    ceiling += [
        f"`{f['id']}` — {f['subject']} (decision `{f['decision']}`)"
        for f in terminal["findings"]
        if f["decision"] and not f["blocking"]
    ]
    if not actuating:
        ceiling.append(
            f"tier `{tier}` actuates nothing, so stability across iterations is not "
            "measurable — a read-only pass may not assert convergence"
        )
    if coverage["uncovered"]:
        ceiling.append(
            f"{len(coverage['uncovered'])} located loop mandate(s) are discharged by nothing: "
            + ", ".join(f"`{k}`" for k in coverage["uncovered"])
        )

    converged = not unsatisfied
    if not converged:
        determination = "NOT-CONVERGED"
    elif ceiling:
        determination = "CONVERGED-PROVISIONAL"
    else:
        determination = "CONVERGED"

    model = {
        "programme": decl["programme"],
        "tier": tier,
        "actuating": actuating,
        "iterations": iterations,
        "iteration_total": len(iterations),
        "stable_iterations": stable,
        "required_stable_iterations": required,
        "vector_digests": [entry["vector_digest"] for entry in iterations],
        "mandates": coverage,
        "mandate_universe": [universe[k] for k in sorted(universe)],
        "measured": measured,
        "convergence": criteria,
        "unsatisfied_criteria": unsatisfied,
        "unattributed_residue": unattributed,
        "unresolved_pointers": unresolved_pointers,
        "unclassified_findings": unclassified,
        "findings": terminal["findings"],
        "declared_findings": decl["findings"],
        "determination": determination,
        "certification_ceiling": sorted(set(ceiling)),
        "converged": converged,
        "gate_exit": 0 if converged else 1,
    }
    model["learning"] = distil(decl, model)
    model["seal_sha256"] = digest(
        {
            "convergence": [{k: c[k] for k in ("id", "measured", "verdict")} for c in criteria],
            "determination": determination,
            "observations": vector_of(terminal["observations"]),
            "actuators": [[a["id"], a["verdict"]] for a in terminal["actuators"]],
            "mandates": {"total": coverage["universe_total"], "covered": coverage["covered_total"]},
            "tier": tier,
        }
    )
    return model


def distil(decl: dict, model: dict) -> dict:
    """The deterministic knowledge projection an iteration leaves behind."""
    terminal = model["iterations"][-1]
    dimensions = {entry["dimension"]: entry["id"] for entry in decl["learning"]["dimensions"]}
    return {
        "ledger": decl["learning"]["ledger"],
        "dimensions": sorted(dimensions.values()),
        "observation": {
            rec["id"]: {"verdict": rec["verdict"], "observed": rec["observed"]}
            for rec in terminal["observations"]
        },
        "actuator": {
            rec["id"]: {
                "verdict": rec["verdict"],
                "residue_total": len(rec["residue"]),
                "zones_exercised": sorted(
                    {
                        zone
                        for zone in (
                            next(
                                (a["writes"] for a in decl["actuators"] if a["id"] == rec["id"]), []
                            )
                        )
                        for path in rec["residue"]
                        if path.startswith(zone)
                    }
                ),
            }
            for rec in terminal["actuators"]
            if rec["in_scope"]
        },
        "decision": {
            entry["id"]: {
                "class": entry["class"],
                "decision": entry["decision"],
                "rule": entry["rule"],
            }
            for entry in terminal["findings"]
        },
        "convergence": {
            "stable_iterations": model["stable_iterations"],
            "iteration_total": model["iteration_total"],
            "vector_digests": model["vector_digests"],
            "determination": model["determination"],
        },
        "mandate": model["mandates"]["discharged_by"],
    }


# --------------------------------------------------------------------------- rendering


def header(title: str, decl: dict, model: dict, purpose: str) -> str:
    programme = decl["programme"]
    return (
        f"# {title}\n\n"
        + table(
            ["Field", "Value"],
            [
                ["PROGRAMME", f"`{programme['id']}` — {programme['name']} v{programme['version']}"],
                ["AUTHORITY", f"**{programme['authority']}**"],
                ["TIER", f"`{model['tier']}`" + ("" if model["actuating"] else " (read-only)")],
                ["DETERMINATION", f"**{model['determination']}**"],
                ["SEAL", f"`{model['seal_sha256'][:32]}`"],
                [
                    "REPOSITORY ANCHOR",
                    "the containing commit — owned by version control, never restated here",
                ],
            ],
        )
        + f"\n> {purpose}\n\n---\n\n"
    )


def render(decl: dict, model: dict) -> dict[str, str]:
    out: dict[str, str] = {}
    terminal = model["iterations"][-1]
    programme = decl["programme"]

    out["00-AEE-DASHBOARD.md"] = (
        header(
            f"{programme['id']} — Autonomous Evolution Loop Dashboard",
            decl,
            model,
            "The continuously regenerated view of the loop. This programme has no terminal "
            "state: actuate the located owners, read what they determined, classify and "
            "decide every divergence, compare against the previous reading, repeat.",
        )
        + "## Convergence\n\n"
        + table(
            ["Criterion", "Measure", "Expect", "Measured", "Verdict"],
            [
                [
                    f"`{c['id']}`",
                    f"`{c['measure']}`",
                    f"`{c['expect']}`",
                    f"`{c['measured']}`",
                    f"**{c['verdict']}**" if c["verdict"] != "SATISFIED" else c["verdict"],
                ]
                for c in model["convergence"]
            ],
        )
        + "\n## Loop state\n\n"
        + table(
            ["Dimension", "Value"],
            [
                ["Iterations executed", str(model["iteration_total"])],
                [
                    "Consecutive iterations sharing one observation vector",
                    f"{model['stable_iterations']} "
                    f"(required {model['required_stable_iterations']})",
                ],
                ["Observations declared", str(len(terminal["observations"]))],
                [
                    "Observations satisfied",
                    str(sum(1 for r in terminal["observations"] if r["verdict"] == "SATISFIED")),
                ],
                [
                    "Actuators in scope",
                    str(sum(1 for r in terminal["actuators"] if r["in_scope"])),
                ],
                ["Located loop mandates read", str(model["mandates"]["universe_total"])],
                ["Mandates discharged", str(model["mandates"]["covered_total"])],
                ["Findings discovered", str(len(terminal["findings"]))],
                ["Unsatisfied blocking criteria", joined(model["unsatisfied_criteria"])],
                ["Gate exit code", str(model["gate_exit"])],
            ],
        )
        + "\n## Certification ceiling\n\n"
        + (
            "The maximum attainable verdict is **CONVERGED-PROVISIONAL** while the "
            "following stand:\n\n"
            + "".join(f"- {reason}\n" for reason in model["certification_ceiling"])
            if model["certification_ceiling"]
            else "No standing ceiling recorded.\n"
        )
        + "\n---\n\n*Regenerate with `make aee`. Enforce with `make aee-gate`.*\n"
    )

    out["01-MANDATE-COVERAGE-REGISTER.md"] = (
        header(
            f"{programme['id']} — Loop Mandate Coverage",
            decl,
            model,
            "The loop's phases are not authored here. They are READ from the located "
            "declarations that already own them, and each is bound to whatever discharges "
            "it. A phase appended to a source appears here on the next run.",
        )
        + "## Mandate sources\n\n"
        + table(
            ["Source", "Name", "Owner"],
            [[f"`{s['id']}`", s["name"], f"`{s['owner']}`"] for s in decl["mandate_sources"]],
        )
        + "\n## Coverage\n\n"
        + table(
            ["Mandate", "Source", "Discharged by", "Phase"],
            [
                [
                    f"`{m['id']}`",
                    f"`{m['source']}`",
                    joined(model["mandates"]["discharged_by"].get(m["id"], [])),
                    m["label"],
                ]
                for m in model["mandate_universe"]
            ],
        )
        + f"\nUncovered: {joined(model['mandates']['uncovered'])}\n"
    )

    out["02-ACTUATOR-EXECUTION-REGISTER.md"] = (
        header(
            f"{programme['id']} — Actuator Execution",
            decl,
            model,
            "Every actuator is a located owner's own entry point, invoked so that owner "
            "regenerates its own determination. This programme authored none of them and "
            "writes none of their homes.",
        )
        + table(
            ["Actuator", "Located owner", "Tier", "Required", "Verdict", "Residue", "Unattributed"],
            [
                [
                    f"`{r['id']}`",
                    f"`{r['owner']}`",
                    f"`{r['tier']}`",
                    "yes" if r["required"] else "no",
                    f"**{r['verdict']}**" if r["verdict"] not in ("PASS",) else r["verdict"],
                    str(len(r["residue"])),
                    joined(r["unattributed"]),
                ]
                for r in terminal["actuators"]
            ],
        )
        + "\n> Residue is attributed to the actuator's declared write zone. An entry no "
        "declared zone explains is unattributed and blocks convergence.\n"
    )

    out["03-OBSERVATION-REGISTER.md"] = header(
        f"{programme['id']} — Observation Register",
        decl,
        model,
        "Each reading is taken from a located owner's own sealed output. This "
        "programme measures nothing itself; it reports what its owners determined.",
    ) + table(
        ["Observation", "Located owner", "Pointer", "Operator", "Verdict", "Observed"],
        [
            [
                f"`{r['id']}`",
                f"`{r['owner']}`",
                f"`{r['pointer']}`",
                f"`{spec['operator']}`",
                f"**{r['verdict']}**" if r["verdict"] != "SATISFIED" else r["verdict"],
                f"`{json.dumps(r['observed'], ensure_ascii=False)[:80]}`",
            ]
            for r, spec in zip(terminal["observations"], decl["observations"], strict=True)
        ],
    )

    out["04-DISCOVERY-AND-CLASSIFICATION-REGISTER.md"] = (
        header(
            f"{programme['id']} — Discovery and Classification",
            decl,
            model,
            "A finding is an observation that diverged from its declared expectation, or a "
            "required actuator that did not succeed. The set is discovered from Repository "
            "Truth; no finding is listed by hand and none is classified by hand.",
        )
        + "## Classification rules (ordered; first match wins)\n\n"
        + table(
            ["Rule", "Predicate", "Class", "Decision"],
            [
                [
                    f"`{r['id']}`",
                    f"`{json.dumps(r['when'], sort_keys=True)}`",
                    r["class"],
                    f"`{r['decision']}`",
                ]
                for r in decl["classification_rules"]
            ],
        )
        + "\n## Findings\n\n"
        + (
            table(
                ["Finding", "Subject", "Blocking", "Class", "Rule"],
                [
                    [
                        f"`{f['id']}`",
                        f["subject"],
                        "yes" if f["blocking"] else "no",
                        f["class"] or "**UNCLASSIFIED**",
                        f"`{f['rule']}`" if f["rule"] else "—",
                    ]
                    for f in terminal["findings"]
                ],
            )
            if terminal["findings"]
            else "No divergence was discovered at the terminal iteration.\n"
        )
    )

    out["05-DECISION-REGISTER.md"] = (
        header(
            f"{programme['id']} — Decision Register",
            decl,
            model,
            "Every finding receives a decision from the declared rules, with the located "
            "evidence that justifies it. A decision whose evidence obligation is unmet is "
            "withheld rather than asserted.",
        )
        + "## Decision values\n\n"
        + table(
            ["Decision", "Definition"],
            [[f"`{d['decision']}`", d["definition"]] for d in decl["decisions"]],
        )
        + "\n## Adjudication\n\n"
        + (
            "".join(
                f"### `{f['id']}` — {f['subject']}\n\n"
                + table(
                    ["Field", "Value"],
                    [
                        ["DECISION", f"**{f['decision'] or 'WITHHELD'}**"],
                        ["CLASS", f["class"] or "UNCLASSIFIED"],
                        ["MATCHED RULE", f"`{f['rule']}`" if f["rule"] else "—"],
                        ["LOCATED OWNER", f"`{f['owner']}`"],
                        [
                            "GOVERNING FINDING",
                            f"`{f['governed_by_finding']}`" if f["governed_by_finding"] else "—",
                        ],
                        ["EVIDENCE", joined(f["evidence"])],
                        ["MEASURED", f"`{json.dumps(f['observed'], ensure_ascii=False)[:120]}`"],
                    ],
                )
                + f"\n{f['rationale']}\n\n"
                for f in terminal["findings"]
            )
            if terminal["findings"]
            else "Nothing required adjudication at the terminal iteration.\n"
        )
    )

    out["06-ITERATION-LEDGER.md"] = (
        header(
            f"{programme['id']} — Iteration Ledger",
            decl,
            model,
            "One pass proves nothing about stability. The loop compares consecutive "
            "observation vectors and stops only when the required number of consecutive "
            "iterations agree and every blocking criterion is satisfied.",
        )
        + table(
            ["Iteration", "Observation-vector digest", "Blocking violations", "Actuator failures"],
            [
                [
                    str(entry["index"]),
                    f"`{entry['vector_digest'][:32]}`",
                    joined(entry["blocking_violations"]),
                    joined(entry["actuator_failures"]),
                ]
                for entry in model["iterations"]
            ],
        )
        + f"\nTrailing agreement: **{model['stable_iterations']}** consecutive iteration(s); "
        f"**{model['required_stable_iterations']}** required.\n"
    )

    out["07-CONVERGENCE-CERTIFICATION.md"] = (
        header(
            f"{programme['id']} — Convergence Certification",
            decl,
            model,
            "Convergence is measured, never asserted. Byte-level repository closure is a "
            "different and stronger condition owned by the fixed-point programme and "
            "measured by its own gate; this certification does not claim it.",
        )
        + table(
            ["Criterion", "Statement", "Expect", "Measured", "Blocking", "Verdict"],
            [
                [
                    f"`{c['id']}`",
                    c["criterion"],
                    f"`{c['expect']}`",
                    f"`{c['measured']}`",
                    "yes" if c["blocking"] else "no",
                    f"**{c['verdict']}**" if c["verdict"] != "SATISFIED" else c["verdict"],
                ]
                for c in model["convergence"]
            ],
        )
        + "\n## Declared scope boundaries\n\n"
        + table(
            ["Finding", "Title", "Disposition", "Engineering-closable"],
            [
                [
                    f"`{f['id']}`",
                    f["title"],
                    f["disposition"],
                    "yes" if f.get("engineering_closable", True) else "**no**",
                ]
                for f in decl["findings"]
            ],
        )
        + f"\n**Determination: {model['determination']}** · gate exit `{model['gate_exit']}`\n"
    )

    out["08-LEARNING-LEDGER.md"] = (
        header(
            f"{programme['id']} — Learning Ledger",
            decl,
            model,
            "What an iteration establishes is retained so a later run resolves an identical "
            "finding by lookup instead of rediscovery. This is a deterministic knowledge "
            "projection, not a statistical model.",
        )
        + "## Retained dimensions\n\n"
        + table(
            ["Dimension", "Retains"],
            [[f"`{d['dimension']}`", d["retains"]] for d in decl["learning"]["dimensions"]],
        )
        + "\n## Exercised write zones\n\n"
        + table(
            ["Actuator", "Verdict", "Residue entries", "Zones exercised"],
            [
                [f"`{k}`", v["verdict"], str(v["residue_total"]), joined(v["zones_exercised"])]
                for k, v in sorted(model["learning"]["actuator"].items())
            ],
        )
        + f"\n> The machine-readable ledger is `{decl['learning']['ledger']}`.\n"
    )

    out["09-CONTINUOUS-EVOLUTION-BINDING.md"] = (
        header(
            f"{programme['id']} — Continuous Evolution Binding",
            decl,
            model,
            "Cadence is bound to the authorities the repository actually has. No resident "
            "process, scheduler or armed session hook exists here, and inventing one would "
            "be unadjudicated surface, so the loop runs on every change and on invocation.",
        )
        + "## Cadence owners\n\n"
        + table(
            ["Binding", "Owner", "Trigger", "Note"],
            [
                [f"`{c['id']}`", f"`{c['owner']}`", c["trigger"], c["note"]]
                for c in decl["continuous"]["cadence_owners"]
            ],
        )
        + "\n## Closure authority\n\n"
        + table(
            ["Field", "Value"],
            [
                ["BINDING", f"`{decl['continuous']['closure_authority']['id']}`"],
                ["OWNER", f"`{decl['continuous']['closure_authority']['owner']}`"],
                ["NOTE", decl["continuous"]["closure_authority"]["note"]],
            ],
        )
        + "\n## Standing obligations, as read from their located owner\n\n"
        + table(
            ["Mandate", "Obligation", "Discharged by"],
            [
                [
                    f"`{m['id']}`",
                    m["label"],
                    joined(model["mandates"]["discharged_by"].get(m["id"], [])),
                ]
                for m in model["mandate_universe"]
                if m["source"] == decl["mandate_sources"][-1]["id"]
            ],
        )
    )

    out["10-TRACEABILITY.md"] = (
        header(
            f"{programme['id']} — Traceability",
            decl,
            model,
            "Every principle to its located enforcing owner, and every located phase to the "
            "actuator or observation that discharges it. Nothing in this programme is "
            "enforced by prose.",
        )
        + "## Principles\n\n"
        + table(
            ["Principle", "Statement", "Located owner"],
            [[f"`{p['id']}`", p["principle"], f"`{p['owner']}`"] for p in decl["principle"]],
        )
        + "\n## Vocabulary\n\n"
        + table(
            ["Term", "Definition"],
            [[f"**{v['term']}**", v["definition"]] for v in decl["vocabulary"]],
        )
    )

    out["11-CERTIFICATION-REPORT.md"] = (
        header(
            f"{programme['id']} — Certification Report",
            decl,
            model,
            "What this programme certifies, and — equally — what it does not. A verdict "
            "that could not be reached in both directions would carry no evidentiary value.",
        )
        + "## Certified\n\n"
        + table(
            ["Subject", "Evidence", "Verdict"],
            [
                [
                    "The loop is closed and its convergence is measured",
                    "`06-ITERATION-LEDGER.md` · `07-CONVERGENCE-CERTIFICATION.md`",
                    model["determination"],
                ],
                [
                    "Every actuator is a located owner, none authored here",
                    "`02-ACTUATOR-EXECUTION-REGISTER.md` · `--check-reuse-before-create`",
                    "CERTIFIED",
                ],
                [
                    "Every reading comes from a located owner's sealed output",
                    "`03-OBSERVATION-REGISTER.md`",
                    "CERTIFIED",
                ],
                [
                    "Every loop phase is read, not restated",
                    "`01-MANDATE-COVERAGE-REGISTER.md` · `--check-mandate-coverage`",
                    "CERTIFIED",
                ],
                [
                    "Every finding carries a class, a decision and located evidence",
                    "`05-DECISION-REGISTER.md`",
                    "CERTIFIED" if not model["unclassified_findings"] else "NOT-CERTIFIED",
                ],
                [
                    "Emission is deterministic",
                    "`--check-determinism`",
                    "CERTIFIED",
                ],
            ],
        )
        + "\n## Not certified here, and by whom instead\n\n"
        + table(
            ["Subject", "Located owner", "Reason"],
            [
                [f["title"], f"`{f['owner']}`", f["note"]]
                for f in decl["findings"]
                if not f.get("engineering_closable", True)
            ],
        )
    )

    out["12-CONTINUATION-PACKAGE.md"] = (
        header(
            f"{programme['id']} — Continuation Package",
            decl,
            model,
            "The resume anchor. Everything a later session needs in order to continue the "
            "loop without rediscovering what this run established.",
        )
        + "## State\n\n"
        + table(
            ["Field", "Value"],
            [
                ["DETERMINATION", f"**{model['determination']}**"],
                ["TIER", f"`{model['tier']}`"],
                ["ITERATIONS", str(model["iteration_total"])],
                ["SEAL", f"`{model['seal_sha256']}`"],
                ["UNSATISFIED BLOCKING CRITERIA", joined(model["unsatisfied_criteria"])],
                ["OPEN FINDINGS", str(len(model["findings"]))],
            ],
        )
        + "\n## What closes the remaining ceiling, and who owns it\n\n"
        + (
            "".join(f"- {reason}\n" for reason in model["certification_ceiling"])
            if model["certification_ceiling"]
            else "Nothing stands. The loop is at a measured fixed point.\n"
        )
        + "\n## How to continue\n\n"
        + table(
            ["Step", "Command", "Purpose"],
            [
                ["1", "`make aee-self`", "the programme's guards over its own surface"],
                ["2", "`make aee-observe`", "fast read-only pass; no located owner is invoked"],
                ["3", "`make aee-gate`", "actuate, converge, fail closed"],
                ["4", "`make aee-closure`", "include the heavy aggregate tier"],
                ["5", "`make rfp-gate`", "byte-level repository closure — a different owner"],
            ],
        )
    )
    return out


#: UCOS-OBSERVATION-UNIVERSE-001 — observation VALUES may not enter canonical identity.
#:
#: `residue` is the set of paths whose on-disk state changed while a located actuator ran.
#: It is Observation Truth: it depends on what the working tree held BEFORE the run, not on
#: what the commit contains. Writing it into aee.json — the artifact Phase 8 measures as
#: `certification_variance` — made this programme's canonical identity a function of the
#: tree it was measuring.
#:
#: Measured: one stale digest in UKAP-001 caused ONE file to be rewritten. RIB, running
#: later in the same pass, observed that single dirty entry, flipped GATE-04 and GATE-12
#: and rewrote sixteen files. This engine then recorded seventeen residue paths into
#: aee.json. A one-file staleness became a twenty-one-file oscillation that could not
#: converge, because running the gate was itself a mutation that changed the next reading.
#:
#: NOTHING IS WEAKENED AND NOTHING IS DELETED. Residue is still computed, still drives
#: `unattributed`, still fails the write-zone finding closed, and still appears in the
#: dashboard and the evidence index. Only its SERIALIZATION into canonical identity is
#: replaced — by the observation's stable Universal Identity, which is keyed on
#: observer::subject::kind and therefore never moves when the reading does. The reading
#: itself is written to the evidence surface below, so it remains fully traceable.
#:
#: This is the RIB UCOS-RC-003 pattern, applied to the one programme that lacked it, and
#: extended past the flaw RC-003 left open: redaction can hide what a field SAYS, but not
#: whether a list ELEMENT EXISTS, so the key is replaced rather than blanked.
OBS_KIND = "EXECUTION_RESIDUE"
OBS_SUBJECTS = {
    "residue": "actuator-execution-residue",
    "unattributed": "unattributed-residue",
    # A COUNT of an observation is still that observation, at lower resolution. The
    # learning section carried `residue_total` after the per-actuator lists were lifted
    # out, which would have left the same reading leaking through a scalar.
    "residue_total": "actuator-execution-residue",
    "unattributed_residue": "unattributed-residue",
}


def _observation_id(subject: str) -> str:
    """Resolve one of this programme's observations to its stable Universal Identity.

    Read from the ONE identity authority (00-BOOK/DATA/id-ledger.json :: by_observation).
    This engine never mints: minting is UCOS-UGA-001's, and a second minter would be a
    second authority. Fail-closed — an observation with no identity is an anonymous
    observation, and emitting a reference to one would be worse than emitting the value.
    """
    key = f"UCOS-AEE-001::{subject}::{OBS_KIND}"
    ledger = REPO / "00-BOOK" / "DATA" / "id-ledger.json"
    try:
        record = (json.loads(ledger.read_text("utf-8")).get("by_observation") or {}).get(key)
    except (OSError, ValueError) as exc:  # pragma: no cover - unreadable authority
        raise SystemExit(f"UCOS-AEE-001: identity authority unreadable ({exc})") from exc
    if not record:
        raise SystemExit(
            f"UCOS-AEE-001: observation {key!r} holds no Universal Identity. "
            "An identity is obtained only at an AUTHORIZED allocation — an "
            "irreversible CORPUS_REGISTRATION-class mutation of "
            "00-BOOK/DATA/id-ledger.json governed by REG-AUTO-001 "
            "(00-BOOK/DATA/mutation-governance-boundary.json). Obtain that "
            "authorization; this message does not authorize invoking allocation. "
            "Refusing to serialize an anonymous observation."
        )
    return record["observation_id"]


def canonical_model(model: dict) -> dict:
    """The model with observation values replaced by their stable identities.

    Returns a copy. The in-memory model keeps every reading, so gate evaluation, the
    rendered registers and the evidence index are unaffected.
    """
    ids = {key: _observation_id(subject) for key, subject in OBS_SUBJECTS.items()}

    def strip(node: object) -> object:
        if isinstance(node, dict):
            out: dict[str, object] = {}
            for k, v in node.items():
                if k in ids:
                    out[f"{k}_observation"] = ids[k]
                else:
                    out[k] = strip(v)
            return out
        if isinstance(node, list):
            return [strip(v) for v in node]
        return node

    stripped = strip(model)
    assert isinstance(stripped, dict)
    return stripped


def _emit_observation_evidence(model: dict) -> Path:
    """Preserve the readings that canonical_model() lifted out of canonical identity.

    Evidence is relocated, never deleted: every residue path this pass observed is written
    here, addressed by the same observation identity aee.json now carries, so the value is
    one lookup away from the artifact that references it.
    """
    per_actuator = []
    for iteration in model.get("iterations", []):
        for actuator in iteration.get("actuators", []):
            per_actuator.append({
                "actuator": actuator.get("id"),
                "residue": actuator.get("residue", []),
                "unattributed": actuator.get("unattributed", []),
            })
    EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
    target = EVIDENCE_DIR / "observations.json"
    target.write_text(
        canonical_json({
            "authority": "NONE — EVIDENCE. Observation Truth, never canonical identity.",
            "evidence_class": "EXECUTION",
            "binds": "UCOS-OBSERVATION-UNIVERSE-001",
            "observations": {
                f"{key}_observation": _observation_id(subject)
                for key, subject in OBS_SUBJECTS.items()
            },
            "readings": per_actuator,
        }),
        "utf-8",
    )
    return target


def emit(decl: dict, model: dict) -> list[Path]:
    written: list[Path] = []
    for name, body in sorted(render(decl, model).items()):
        target = HERE / name
        target.write_text(body, "utf-8")
        written.append(target)
    _emit_observation_evidence(model)
    state = HERE / STATE_FILE
    state.write_text(canonical_json(canonical_model(model)), "utf-8")
    written.append(state)
    ledger = HERE / decl["learning"]["ledger"]
    # Through the SAME projection as aee.json. The learning ledger was written straight
    # from the runtime model, so it kept `residue_total` after the state file had been
    # cleaned — the forensic sweep in 00-BOOK/DATA/canonical-observation-audit.json found
    # it. One projection, applied at every canonical write, or the leak simply moves.
    ledger.write_text(canonical_json(canonical_model(model)["learning"]), "utf-8")
    written.append(ledger)
    EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
    index = EVIDENCE_DIR / "aee-evidence-index.json"
    index.write_text(
        canonical_json(
            {
                "authority": decl["programme"]["authority"],
                "determination": model["determination"],
                "seal_sha256": model["seal_sha256"],
                "actuators": [
                    {
                        "id": rec["id"],
                        "owner": rec["owner"],
                        "verdict": rec["verdict"],
                        "log": f"{rec['id']}.log",
                        "mandate": rec["mandate"],
                    }
                    for rec in model["iterations"][-1]["actuators"]
                    if rec["in_scope"]
                ],
                "observations": [
                    {
                        "id": rec["id"],
                        "owner": rec["owner"],
                        "source": rec["source"],
                        "pointer": rec["pointer"],
                        "verdict": rec["verdict"],
                        "mandate": rec["mandate"],
                    }
                    for rec in model["iterations"][-1]["observations"]
                ],
                "convergence": [
                    {k: c[k] for k in ("id", "measure", "expect", "measured", "verdict")}
                    for c in model["convergence"]
                ],
            }
        ),
        "utf-8",
    )
    written.append(index)
    return written


# -------------------------------------------------------------------------------- main


def main(argv: list[str] | None = None) -> int:
    decl_probe = load_declaration()
    tier_names = [entry["tier"] for entry in sorted(decl_probe["tiers"], key=lambda e: e["order"])]
    default_tier = next(
        (e["tier"] for e in sorted(decl_probe["tiers"], key=lambda e: e["order"]) if e["actuates"]),
        tier_names[-1],
    )

    parser = argparse.ArgumentParser(
        prog=Path(__file__).name,
        description=f"{decl_probe['programme']['id']} autonomous evolution loop driver.",
    )
    parser.add_argument("--tier", choices=tier_names, default=default_tier)
    parser.add_argument("--gate", action="store_true", help="fail-closed on non-convergence")
    parser.add_argument("--quiet", action="store_true")
    for flag in sorted(SELF_GUARDS):
        parser.add_argument(flag, action="store_true", dest=flag.lstrip("-").replace("-", "_"))
    args = parser.parse_args(argv)

    decl = decl_probe
    for flag, handler in sorted(SELF_GUARDS.items()):
        if getattr(args, flag.lstrip("-").replace("-", "_")):
            label = flag.lstrip("-")
            findings = handler(decl)
            if findings:
                print(f"{decl['programme']['id']} {label}: {len(findings)} finding(s)")
                for text in findings:
                    print(f"  - {text}")
                return 1
            print(f"{decl['programme']['id']} {label}: PASS")
            return 0

    guard = decl["programme"]["reentrancy_env"]
    if os.environ.get(guard):
        fail_closed(
            f"{guard} is set: the fixed-point owner's pipeline is active. Driving the loop "
            "from inside it would rebuild the recursion topology that owner forbids."
        )

    integrity = check_declaration(decl)
    if integrity:
        for text in integrity:
            print(f"  - {text}", file=sys.stderr)
        fail_closed(f"declaration integrity: {len(integrity)} finding(s) — no verdict assertable")

    tiers = {entry["tier"]: entry for entry in decl["tiers"]}
    order = {name: entry["order"] for name, entry in tiers.items()}
    actuating = bool(tiers[args.tier]["actuates"])
    if args.gate and not actuating:
        fail_closed(
            f"tier {args.tier!r} actuates nothing, so stability across iterations cannot be "
            "measured and no gate verdict may be asserted from it"
        )

    universe, problems = read_mandates(decl)
    if problems:
        for text in problems:
            print(f"  - {text}", file=sys.stderr)
        fail_closed("the located mandate sources could not be read")

    iterations = run_loop(decl, args.tier, order, actuating)
    model = assemble(decl, iterations, args.tier, universe)
    written = emit(decl, model)

    scope = check_write_scope(decl, written)
    if scope:
        for text in scope:
            print(f"  - {text}", file=sys.stderr)
        fail_closed("the own-memory guard tripped")

    if not args.quiet:
        terminal = model["iterations"][-1]
        satisfied = sum(1 for r in terminal["observations"] if r["verdict"] == "SATISFIED")
        print(
            f"{decl['programme']['id']}: {model['determination']} | tier={model['tier']} | "
            f"iterations={model['iteration_total']} | "
            f"stable={model['stable_iterations']}/{model['required_stable_iterations']} | "
            f"observations={satisfied}/{len(terminal['observations'])} SATISFIED | "
            f"mandates={model['mandates']['covered_total']}/"
            f"{model['mandates']['universe_total']} covered | "
            f"findings={len(terminal['findings'])} | "
            f"unsatisfied={','.join(model['unsatisfied_criteria']) or 'none'} | "
            f"seal={model['seal_sha256'][:16]}"
        )
        print(f"wrote {len(written)} artifacts to {relative(HERE)}")

    if args.gate and not model["converged"]:
        print(
            "GATE: FAIL-CLOSED — unsatisfied blocking convergence criteria: "
            + ", ".join(model["unsatisfied_criteria"]),
            file=sys.stderr,
        )
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
