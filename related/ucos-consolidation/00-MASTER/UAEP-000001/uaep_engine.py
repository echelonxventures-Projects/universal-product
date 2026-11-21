#!/usr/bin/env python3
"""UAEP-000001 — the platform capability binding engine.

AUTHORITY = NONE (DERIVED TRUTH). This engine asserts nothing of its own. It reads the
declaration ``uaep-platform.json``, measures every declared binding against Repository
Truth, and renders the registers. Where this output and a canonical owner differ, the
canonical owner governs.

What this engine is for
-----------------------
The platform agreement this programme records names sixteen capabilities. Fifteen of them
already have canonical homes in this repository and one has none. An agreement that lives
only in conversation cannot be verified and cannot be kept true as the repository moves, so
this engine binds each named capability to the home that already realises it and then
*checks that the binding still resolves*. If a bound module is renamed, moved or deleted,
the gate closes.

Every capability name and id lives in the declaration, never here — ``--check-no-enumeration``
fails if one leaks into this source, including into this docstring.

What this engine must never do
------------------------------
It creates no engine, no registry, no catalogue, no identity, no graph and no pipeline. It
enumerates no capability: every capability, home, symbol, vocabulary and validation is read
from the declaration, so adding one is a data edit and is checked by ``--check-no-enumeration``.
It writes only inside its own programme directory, checked by ``--check-write-scope``.

Determinism
-----------
No timestamp, no clock, no environment value and no path outside the repository enters the
output, so two renders of one committed declaration are byte-identical. That is what
``--check-determinism`` proves and it is what lets CI diff a replay against the commit.

Usage:
    uaep_engine.py                     measure and print the determination
    uaep_engine.py --render            measure and write the registers
    uaep_engine.py --gate              fail-closed: exit 1 if any blocking validation fails
    uaep_engine.py --check-declaration        declaration integrity
    uaep_engine.py --check-no-enumeration     no capability data is hardcoded in this engine
    uaep_engine.py --check-write-scope        writes stay inside this programme
    uaep_engine.py --check-determinism        two renders are byte-identical
    uaep_engine.py --check-reuse-before-create no binding points inside this programme
    uaep_engine.py --check-open-world         every declared vocabulary is open

Exit codes: 0 satisfied / gate OPEN · 1 gate CLOSED or self-guard failed · 2 fail-closed
abort (the declaration itself is unusable, so no determination is assertable).
"""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
DECLARATION = HERE / "uaep-platform.json"
MODEL = HERE / "uaep.json"

#: The repo-relative prefix this programme owns. Nothing outside it is ever written, and no
#: binding may point inside it (that would be this programme realising its own capability).
OWN_PREFIX = f"{HERE.relative_to(REPO).as_posix()}/"

CATALOGUE = "intelligence/UCOS-RIE-CAPABILITY-CATALOG.json"


class FailClosed(Exception):
    """The declaration or its substrate is unusable, so no verdict may be asserted."""


# ---------------------------------------------------------------------------------
# substrate
# ---------------------------------------------------------------------------------
def load_declaration() -> dict[str, Any]:
    """Read the declaration, failing closed rather than guessing at a broken one."""
    if not DECLARATION.is_file():
        raise FailClosed(f"required declaration absent: {DECLARATION.relative_to(REPO)}")
    try:
        document = json.loads(DECLARATION.read_text("utf-8"))
    except json.JSONDecodeError as exc:
        raise FailClosed(f"declaration is not valid JSON: {exc}") from exc
    if not isinstance(document, dict):
        raise FailClosed("declaration must be a JSON object")
    for key in ("programme", "dispositions", "vocabularies", "capabilities", "validations"):
        if key not in document:
            raise FailClosed(f"declaration is missing the required key '{key}'")
    return document


def module_symbols(path: Path) -> set[str]:
    """Top-level names bound by a Python module, read without importing it.

    Importing would execute the module and make this engine depend on the very code it is
    measuring. Parsing keeps the measurement inert. ``AnnAssign`` matters as much as
    ``Assign``: an annotated module constant is still a bound name.
    """
    try:
        tree = ast.parse(path.read_text("utf-8", errors="replace"), filename=str(path))
    except (SyntaxError, OSError):
        return set()
    names: set[str] = set()
    for node in tree.body:
        if isinstance(node, ast.ClassDef | ast.FunctionDef | ast.AsyncFunctionDef):
            names.add(node.name)
        elif isinstance(node, ast.Assign):
            names.update(t.id for t in node.targets if isinstance(t, ast.Name))
        elif isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
            names.add(node.target.id)
    return names


def seed_pipeline_types(document: dict[str, Any]) -> set[str]:
    """The pipeline categories the framework seeds, read from its source as data.

    The seed set is derived from the framework's own module rather than restated here, so
    this programme cannot drift out of agreement with the vocabulary it is checking.
    """
    vocabulary = next(
        (v for v in document["vocabularies"] if v.get("seed_symbol")),
        None,
    )
    if vocabulary is None:
        return set()
    home = REPO / str(vocabulary["registrar_home"])
    symbol = str(vocabulary["seed_symbol"])
    if not home.is_file():
        return set()
    try:
        tree = ast.parse(home.read_text("utf-8", errors="replace"), filename=str(home))
    except (SyntaxError, OSError):
        return set()
    for node in tree.body:
        target = None
        if isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
            target = node.target.id
        elif isinstance(node, ast.Assign):
            target = next((t.id for t in node.targets if isinstance(t, ast.Name)), None)
        if target != symbol:
            continue
        found: set[str] = set()
        for element in ast.walk(node):
            if isinstance(element, ast.Tuple) and element.elts:
                first = element.elts[0]
                if isinstance(first, ast.Constant) and isinstance(first.value, str):
                    found.add(first.value)
        return found
    return set()


def catalogue_records() -> dict[str, dict[str, Any]]:
    """The canonical capability catalogue, keyed by its unique id."""
    path = REPO / CATALOGUE
    if not path.is_file():
        return {}
    try:
        document = json.loads(path.read_text("utf-8"))
    except json.JSONDecodeError:
        return {}
    return {
        str(record.get("unique_id")): record
        for record in document.get("capabilities", [])
        if record.get("unique_id")
    }


# ---------------------------------------------------------------------------------
# measurement
# ---------------------------------------------------------------------------------
def measure(document: dict[str, Any]) -> dict[str, Any]:
    """Measure every declared binding against Repository Truth.

    Returns the machine model. Every field is derived; nothing is asserted.
    """
    capabilities = document["capabilities"]
    dispositions = {str(d["id"]) for d in document["dispositions"]}
    catalogue = catalogue_records()
    seeded = seed_pipeline_types(document)
    declared_types = [str(t) for t in document.get("declared_pipeline_types", [])]

    missing_homes: list[str] = []
    missing_catalogue: list[str] = []
    missing_symbols: list[str] = []
    inside_own: list[str] = []
    bad_disposition: list[str] = []
    unbound: list[str] = []
    undisclosed_gaps: list[str] = []
    bindings: list[dict[str, Any]] = []

    for capability in capabilities:
        identifier = str(capability.get("id", ""))
        homes = [str(h) for h in capability.get("homes", [])]
        symbols = [str(s) for s in capability.get("symbols", [])]
        disposition = str(capability.get("disposition", ""))

        if not homes:
            unbound.append(identifier)
        if disposition not in dispositions:
            bad_disposition.append(f"{identifier}:{disposition or 'NONE'}")

        resolved: list[str] = []
        for home in homes:
            if home.startswith(OWN_PREFIX):
                inside_own.append(f"{identifier}:{home}")
            if (REPO / home).exists():
                resolved.append(home)
            else:
                missing_homes.append(f"{identifier}:{home}")

        available: set[str] = set()
        for home in resolved:
            if home.endswith(".py"):
                available |= module_symbols(REPO / home)
        for symbol in symbols:
            if symbol not in available:
                missing_symbols.append(f"{identifier}:{symbol}")

        prohibited = False
        for record_id in (str(c) for c in capability.get("catalogue_ids", [])):
            record = catalogue.get(record_id)
            if record is None:
                missing_catalogue.append(f"{identifier}:{record_id}")
                continue
            if record.get("replacement_prohibited"):
                prohibited = True

        gap = str(capability.get("gap", ""))
        if gap and len(gap.split()) < 4:
            undisclosed_gaps.append(identifier)

        bindings.append(
            {
                "id": identifier,
                "name": str(capability.get("name", "")),
                "disposition": disposition,
                "homes": homes,
                "homes_resolved": len(resolved),
                "homes_declared": len(homes),
                "symbols": symbols,
                "catalogue_ids": [str(c) for c in capability.get("catalogue_ids", [])],
                "replacement_prohibited": prohibited,
                "gap": gap,
            }
        )

    # An identical home set for two capabilities would be two authorities over one home.
    seen: dict[str, str] = {}
    duplicate_bindings: list[str] = []
    for binding in bindings:
        key = "|".join(sorted(binding["homes"]))
        if not key:
            continue
        if key in seen:
            duplicate_bindings.append(f"{seen[key]}={binding['id']}")
        else:
            seen[key] = binding["id"]

    unseeded_types = sorted(t for t in declared_types if t not in seeded) if seeded else []

    closed_vocabularies: list[str] = []
    for vocabulary in document["vocabularies"]:
        if not vocabulary.get("open", False):
            closed_vocabularies.append(str(vocabulary["id"]))
            continue
        home = REPO / str(vocabulary["registrar_home"])
        registrar = str(vocabulary["registrar"])
        if not home.is_file() or registrar not in module_symbols(home):
            closed_vocabularies.append(f"{vocabulary['id']}:{registrar}")

    # A capability bound to a record whose replacement is prohibited must actually reuse it:
    # naming a protected owner while resolving none of its homes would be a claim of reuse
    # with nothing behind it.
    unreused_protected = sorted(
        f"{b['id']}:0/{b['homes_declared']}"
        for b in bindings
        if b["replacement_prohibited"] and b["homes_resolved"] == 0
    )

    # The measurement binding: declared validation id -> measured failures. This is the one
    # place the engine names a validation, because each dimension needs its own measurement
    # and measurement logic cannot be derived from data. It is kept honest by the parity check
    # below: a declared validation with no measurement here FAILS CLOSED rather than being
    # reported satisfied, because absence of evidence is never evidence.
    findings: dict[str, list[str]] = {
        "UAEP-VAL-01": sorted(missing_homes),
        "UAEP-VAL-02": sorted(missing_catalogue),
        "UAEP-VAL-03": sorted(missing_symbols),
        "UAEP-VAL-04": sorted(inside_own),
        "UAEP-VAL-05": sorted(bad_disposition),
        "UAEP-VAL-06": sorted(unbound),
        "UAEP-VAL-07": sorted(closed_vocabularies),
        "UAEP-VAL-08": unseeded_types,
        "UAEP-VAL-09": sorted(duplicate_bindings),
        "UAEP-VAL-10": unreused_protected,
        "UAEP-VAL-11": sorted(undisclosed_gaps),
    }

    validations: list[dict[str, Any]] = []
    for declared in document["validations"]:
        identifier = str(declared["id"])
        measured = identifier in findings
        failures = findings.get(identifier, [f"{identifier}: declared but never measured"])
        validations.append(
            {
                "id": identifier,
                "dimension": str(declared["dimension"]),
                "obligation": str(declared["obligation"]),
                "blocking": bool(declared.get("blocking", True)),
                "measured": measured,
                "satisfied": measured and not failures,
                "failures": failures if not measured or failures else [],
            }
        )

    blocking_failed = [v["id"] for v in validations if v["blocking"] and not v["satisfied"]]
    counts = {
        "capabilities": len(bindings),
        "homes_declared": sum(b["homes_declared"] for b in bindings),
        "homes_resolved": sum(b["homes_resolved"] for b in bindings),
        "symbols_declared": sum(len(b["symbols"]) for b in bindings),
        "reuse": sum(1 for b in bindings if b["disposition"] == "REUSE"),
        "extend": sum(1 for b in bindings if b["disposition"] == "EXTEND"),
        "compose": sum(1 for b in bindings if b["disposition"] == "COMPOSE"),
        "gaps_disclosed": sum(1 for b in bindings if b["gap"]),
        "pipeline_types_declared": len(declared_types),
        "pipeline_types_seeded": len(seeded),
        "validations": len(validations),
        "validations_measured": sum(1 for v in validations if v["measured"]),
        "validations_satisfied": sum(1 for v in validations if v["satisfied"]),
    }

    model: dict[str, Any] = {
        "programme": document["programme"],
        "bindings": bindings,
        "counts": counts,
        "validations": validations,
        "blocking_failures": blocking_failed,
        "gate": "CLOSED" if blocking_failed else "OPEN",
        "determination": (
            "PLATFORM NOT BOUND — REPOSITORY MUST STOP"
            if blocking_failed
            else "PLATFORM BOUND — EVERY NAMED CAPABILITY RESOLVES IN REPOSITORY TRUTH"
        ),
        "exit_criteria": document.get("exit_criteria", []),
    }
    model["seal_sha256"] = hashlib.sha256(
        json.dumps(model, sort_keys=True, ensure_ascii=False).encode("utf-8")
    ).hexdigest()
    return model


# ---------------------------------------------------------------------------------
# rendering
# ---------------------------------------------------------------------------------
def _table(rows: list[list[str]], header: list[str]) -> list[str]:
    lines = ["| " + " | ".join(header) + " |", "|" + "|".join(["---"] * len(header)) + "|"]
    lines.extend("| " + " | ".join(row) + " |" for row in rows)
    return lines


def render(model: dict[str, Any]) -> dict[str, str]:
    """Build every register as text. Pure: no clock, no environment, no I/O."""
    programme = model["programme"]
    counts = model["counts"]
    pages: dict[str, str] = {}

    head = [
        f"# {programme['name']}",
        "",
        "| Field | Value |",
        "|---|---|",
        f"| PROGRAMME | `{programme['id']}` |",
        f"| VERSION | {programme['version']} |",
        f"| AUTHORITY | **{programme['authority']}** |",
        f"| GOVERNING INSTRUMENT | `{programme['governing_instrument']}` |",
        f"| CAPABILITIES BOUND | {counts['capabilities']} |",
        f"| HOMES RESOLVED | {counts['homes_resolved']}/{counts['homes_declared']} |",
        f"| SYMBOLS VERIFIED | {counts['symbols_declared']} |",
        f"| DISPOSITIONS | REUSE {counts['reuse']} · EXTEND {counts['extend']}"
        f" · COMPOSE {counts['compose']} |",
        f"| VALIDATIONS | {counts['validations_satisfied']}/{counts['validations']} |",
        f"| GATE | **{model['gate']}** |",
        f"| DETERMINATION | **{model['determination']}** |",
        f"| SEAL (sha256) | `{model['seal_sha256']}` |",
        "| GENERATED BY | `uaep_engine.py` — regenerated, never hand-authored |",
        "",
        "> " + programme["disclosure"],
        "",
    ]
    pages["00-UAEP-DASHBOARD.md"] = "\n".join(
        head
        + [
            "## Why this register exists",
            "",
            "The platform agreement names sixteen capabilities. Fifteen already had a canonical",
            "home before this programme existed and one had none. This register binds each name to",
            "the home that realises it and then proves the binding still resolves, so a rename, a",
            "move or a deletion closes the gate instead of quietly invalidating the agreement.",
            "",
            "Nothing here is a new engine. The one capability with no home is discharged by",
            "composition over homes that already exist, and that absence is recorded rather than",
            "closed by building a sixteenth engine.",
            "",
        ]
    )

    rows = [
        [
            f"`{b['id']}`",
            b["name"],
            f"**{b['disposition']}**",
            f"{b['homes_resolved']}/{b['homes_declared']}",
            ", ".join(f"`{h}`" for h in b["homes"]),
            ", ".join(b["catalogue_ids"]) or "—",
        ]
        for b in model["bindings"]
    ]
    pages["01-CAPABILITY-BINDING-REGISTER.md"] = "\n".join(
        [
            "# Capability Binding Register",
            "",
            f"> AUTHORITY = {programme['authority']}. Exactly one binding per named capability,",
            "> and the proof that every bound home resolves in Repository Truth.",
            "",
            *_table(
                rows,
                ["ID", "Capability", "Disposition", "Homes", "Bound to", "Catalogue"],
            ),
            "",
            "## Reuse rationale, per capability",
            "",
        ]
        + [
            line
            for b in model["bindings"]
            for line in (f"### {b['id']} — {b['name']}", "", f"{_rationale(b)}", "")
        ]
    )

    validation_rows = [
        [
            f"`{v['id']}`",
            v["dimension"],
            "**PASS**" if v["satisfied"] else "**FAIL**",
            "blocking" if v["blocking"] else "advisory",
            "yes" if v["measured"] else "**NOT MEASURED**",
            ", ".join(f"`{f}`" for f in v["failures"][:6]) or "—",
        ]
        for v in model["validations"]
    ]
    pages["02-VALIDATION-REPORT.md"] = "\n".join(
        [
            "# Validation Report",
            "",
            f"> Every dimension is measured from Repository Truth. Seal `{model['seal_sha256']}`.",
            "",
            *_table(
                validation_rows,
                ["ID", "Dimension", "Result", "Class", "Measured", "Failures"],
            ),
            "",
            f"**Measured:** {counts['validations_measured']}/{counts['validations']}"
            " — a declared dimension with no measurement fails closed, because absence of"
            " evidence is never evidence.",
            "",
            f"**Blocking failures:** {len(model['blocking_failures'])}"
            f" {model['blocking_failures'] or ''}".rstrip(),
            "",
        ]
    )

    criteria_rows = [
        [f"`{c['id']}`", str(c["criterion"]), "**MET**" if model["gate"] == "OPEN" else "**UNMET**"]
        for c in model["exit_criteria"]
    ]
    pages["03-CERTIFICATION-REPORT.md"] = "\n".join(
        [
            "# Certification Report",
            "",
            f"| GATE | **{model['gate']}** |",
            "|---|---|",
            f"| DETERMINATION | **{model['determination']}** |",
            f"| SEAL (sha256) | `{model['seal_sha256']}` |",
            "",
            *_table(criteria_rows, ["ID", "Exit criterion", "Standing"]),
            "",
            "> **Standing.** CERTIFIED-PROVISIONAL. This programme holds no ratification",
            "> authority: it measures bindings and reports. Where this register and a canonical",
            "> owner differ, the canonical owner governs.",
            "",
        ]
    )
    return pages


def _rationale(binding: dict[str, Any]) -> str:
    parts = [f"Disposition **{binding['disposition']}**."]
    if binding["replacement_prohibited"]:
        parts.append(
            "The bound catalogue record prohibits replacement, so this capability is bound by "
            "pointer and never re-implemented."
        )
    if binding["gap"]:
        parts.append(f"Recorded gap: {binding['gap']}")
    return " ".join(parts)


def write_registers(model: dict[str, Any]) -> list[str]:
    """Write the registers. Every path is inside this programme's own directory."""
    written: list[str] = []
    for name, text in sorted(render(model).items()):
        target = HERE / name
        body = text if text.endswith("\n") else text + "\n"
        target.write_text(body, "utf-8")
        written.append(name)
    MODEL.write_text(
        json.dumps(model, indent=2, sort_keys=True, ensure_ascii=False) + "\n", "utf-8"
    )
    written.append(MODEL.name)
    return written


# ---------------------------------------------------------------------------------
# self-guards
# ---------------------------------------------------------------------------------
def check_declaration(document: dict[str, Any]) -> list[str]:
    problems: list[str] = []
    seen: set[str] = set()
    for capability in document["capabilities"]:
        identifier = str(capability.get("id", ""))
        if not identifier:
            problems.append("a capability carries no id")
        if identifier in seen:
            problems.append(f"duplicate capability id: {identifier}")
        seen.add(identifier)
        for field in ("name", "disposition", "objective", "reuse"):
            if not str(capability.get(field, "")).strip():
                problems.append(f"{identifier}: '{field}' is empty")
    declared = {str(v["id"]) for v in document["validations"]}
    if len(declared) != len(document["validations"]):
        problems.append("duplicate validation id")
    return problems


def check_no_enumeration(document: dict[str, Any]) -> list[str]:
    """This engine must contain no capability data. Adding a capability is a data edit."""
    source = Path(__file__).read_text("utf-8")
    leaked: list[str] = []
    for capability in document["capabilities"]:
        for field in ("id", "name"):
            value = str(capability.get(field, ""))
            if value and value in source:
                leaked.append(f"{field}={value}")
    for vocabulary in document["vocabularies"]:
        if str(vocabulary["id"]) in source:
            leaked.append(f"vocabulary={vocabulary['id']}")
    return leaked


def check_write_scope() -> list[str]:
    """Every write target must resolve inside this programme's own directory."""
    problems: list[str] = []
    targets = [HERE / name for name in render(measure(load_declaration()))] + [MODEL]
    for target in targets:
        try:
            target.resolve().relative_to(HERE)
        except ValueError:
            problems.append(str(target))
    return problems


def check_determinism() -> list[str]:
    first = render(measure(load_declaration()))
    second = render(measure(load_declaration()))
    return sorted(k for k in first if first[k] != second.get(k))


def check_reuse_before_create(model: dict[str, Any]) -> list[str]:
    return [
        f"{b['id']}:{home}"
        for b in model["bindings"]
        for home in b["homes"]
        if home.startswith(OWN_PREFIX)
    ]


def check_open_world(model: dict[str, Any]) -> list[str]:
    validation = next(
        (v for v in model["validations"] if "vocabular" in v["dimension"].lower()), None
    )
    return list(validation["failures"]) if validation else ["no vocabulary dimension declared"]


# ---------------------------------------------------------------------------------
# entry point
# ---------------------------------------------------------------------------------
GUARDS = (
    "--check-declaration",
    "--check-no-enumeration",
    "--check-write-scope",
    "--check-determinism",
    "--check-reuse-before-create",
    "--check-open-world",
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="uaep_engine.py",
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--render", action="store_true", help="write the registers")
    parser.add_argument("--gate", action="store_true", help="fail-closed: exit 1 if closed")
    parser.add_argument("--quiet", action="store_true")
    for flag in GUARDS:
        parser.add_argument(flag, action="store_true", dest=flag[2:].replace("-", "_"))
    args = parser.parse_args(argv)

    try:
        document = load_declaration()
    except FailClosed as exc:
        print(f"FAIL-CLOSED ABORT — {exc}", file=sys.stderr)
        return 2

    guard_results: list[tuple[str, list[str]]] = []
    if args.check_declaration:
        guard_results.append(("check-declaration", check_declaration(document)))
    if args.check_no_enumeration:
        guard_results.append(("check-no-enumeration", check_no_enumeration(document)))
    if args.check_write_scope:
        guard_results.append(("check-write-scope", check_write_scope()))
    if args.check_determinism:
        guard_results.append(("check-determinism", check_determinism()))

    model = measure(document)

    if args.check_reuse_before_create:
        guard_results.append(("check-reuse-before-create", check_reuse_before_create(model)))
    if args.check_open_world:
        guard_results.append(("check-open-world", check_open_world(model)))

    if guard_results:
        failed = 0
        for name, problems in guard_results:
            status = "PASS" if not problems else "FAIL"
            print(f"UAEP-000001 {name}: {status}")
            for problem in problems[:20]:
                print(f"  - {problem}")
            failed += 1 if problems else 0
        return 1 if failed else 0

    if args.render:
        written = write_registers(model)
        if not args.quiet:
            print(f"wrote {len(written)} artifacts to {HERE.relative_to(REPO)}")

    counts = model["counts"]
    if not args.quiet:
        print(
            f"UAEP-000001: {model['determination']}"
            f" | capabilities={counts['capabilities']}"
            f" | homes={counts['homes_resolved']}/{counts['homes_declared']}"
            f" | symbols={counts['symbols_declared']}"
            f" | reuse={counts['reuse']} extend={counts['extend']} compose={counts['compose']}"
            f" | validations={counts['validations_satisfied']}/{counts['validations']}"
            f" | gate={model['gate']}"
            f" | seal={model['seal_sha256'][:12]}"
        )
        for failure in model["blocking_failures"]:
            print(f"  BLOCKING FAIL: {failure}")

    if args.gate and model["gate"] != "OPEN":
        return 1
    return 0


if __name__ == "__main__":  # pragma: no cover - CLI
    raise SystemExit(main())
