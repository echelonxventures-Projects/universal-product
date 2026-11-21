"""EX-018 — the fail-closed gate over the mutation governance boundary.

WHY THIS FILE EXISTS, STATED AS THE MEASUREMENT THAT PRODUCED IT. EX-015 made the mutation
rules declarative and EX-016 made them decidable, and then nothing decided with them. A
repository-wide search for importers of ``mutation_classification`` returned exactly one file
outside the module itself: its own test. No Makefile target, no workflow and no ``verify.sh``
stage ever called :func:`classify`. Neither the classifier nor the register it reads appeared
among UEC-000001's 172 governed enforcement artifacts, so both could have been deleted outright
with every gate in the repository still green.

That is the defect class UEC-L-04 refuses — *"nothing enforces by existing"* — occurring in the
one subsystem UEC's own discovery rules did not reach. It is also why R-09 stayed broken for so
long in two different ways: first declared with no predicate at all, so ``classify()`` returned
ERROR for **every** subject in the corpus; then implemented but unreachable, so
``GOVERNED_ANALYSIS`` claimed 0 of 6751 tracked paths. Both states passed every gate the
repository had, because no gate asked.

WHAT THIS GATE ADDS NO AUTHORITY OVER. It owns no mutation class, writes no register and
decides no artifact's owner. It reads ``00-BOOK/DATA/mutation-governance-boundary.json`` and
reports whether that register is still decidable. H-06/CR-09 owns the boundary; this measures it.

THE THREE LAWS ARE DECLARED IN THE REGISTER, not held as a table here — ``gate.laws`` in
``00-BOOK/DATA/mutation-governance-boundary.json``. A law table constant in this module would
be a second vocabulary beside the register, extendable only by a code edit. :func:`measure`
binds the two sides in both directions: a declared law with no measurement, and a measurement
no law declares, are each a FAULT. What each law is for:

  MGB-L-01  COVERAGE      — every declared rule has a predicate, and every predicate a rule.
                            A declared rule nobody evaluates is prose; an implemented predicate
                            no rule declares is dead code wearing the appearance of enforcement.
  MGB-L-02  REACHABILITY  — no declared rule is shadowed by an earlier one, and precedence is a
                            total order. Coverage cannot see this: R-09 was declared, implemented,
                            covered and could never fire.
  MGB-L-03  POPULATION    — every declared rule actually claims a subject over the live corpus,
                            or the register names it in ``$rules_expected_to_claim_no_tracked_path``
                            with a reason. Reachable in principle is not reached in fact.

Collapsing any two would hide a defect the other detects. L-01 and L-02 are static and hold for
any repository; L-03 is a census of this one.

UNRESOLVED IS REPORTED, NOT REFUSED. The terminal population is a governance question with an
owner, not a defect this gate may decide: refusing on it would have this gate legislate a policy
nobody has adopted. It is printed on every run, and on the JSON surface, so it cannot be quietly
forgotten — but it does not move the verdict.

OBSERVE MODE. This module writes nothing, reads no clock and takes no environment. Two runs over
one repository state produce identical bytes.

EXIT CODES. ``0`` OPEN, ``1`` CLOSED (a law was measured and refused), ``2`` FAULT (no verdict
could be reached — the register is absent or unreadable). Exit 1 and exit 2 are deliberately
different answers: collapsing them would let an unreadable register pass as whichever answer
happened to be convenient.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from platform.repository_intelligence.mutation_classification import (
    BOUNDARY_PATH,
    CLASSIFIED,
    UNRESOLVED,
    ClassificationError,
    Repository,
    classify_all,
    load_boundary,
    ordered_rules,
    validate_rule_coverage,
    validate_rule_population,
    validate_rule_reachability,
)

EXIT_OPEN = 0
EXIT_CLOSED = 1
EXIT_FAULT = 2


def measure(root: Path | None = None) -> dict:
    """Measure every law over one repository state. Raises :class:`ClassificationError` on FAULT.

    The census is computed once and shared by L-03 and the report: classifying 6700 subjects
    twice would double the cost of the only expensive step and could not disagree with itself
    usefully.
    """
    repository = Repository(root=Path(root) if root is not None else Path.cwd())
    boundary = load_boundary(repository.root)

    coverage = validate_rule_coverage(boundary)
    # Reachability is already folded into `validate_rule_coverage`, which returns coverage
    # problems alone when any exist — reading criteria functions for a rule that has no
    # predicate is not yet meaningful. Ask for it separately so the report attributes each
    # refusal to the law that found it rather than to whichever ran first.
    reachability = validate_rule_reachability(boundary) if not coverage else ()

    results: tuple = ()
    population: tuple[str, ...] = ()
    if not coverage and not reachability:
        results = classify_all(sorted(repository.tracked), repository)
        population = validate_rule_population(results, boundary)

    # Law id to the measurement that decides it. LOCAL, not a module-level table: the register
    # declares WHICH laws exist and this names HOW each is measured, and the two are bound in
    # both directions immediately below — a declared law nothing measures cannot be evaluated,
    # and a measurement no law declares is a verdict attributable to nothing. Same two-sided
    # construction the classifier uses for rules and predicates.
    findings = {
        "MGB-L-01": list(coverage),
        "MGB-L-02": list(reachability),
        "MGB-L-03": list(population),
    }
    declared = boundary.get("gate", {}).get("laws") or ()
    titles = {str(law.get("law_id", "")): str(law.get("title", "")) for law in declared}
    if not titles:
        raise ClassificationError(
            f"{BOUNDARY_PATH} declares no gate.laws, so no law could be attributed to a "
            "declaration and the verdict would be this module's opinion rather than a "
            "measurement of the register"
        )
    for law_id in sorted(set(titles) - set(findings)):
        raise ClassificationError(
            f"{BOUNDARY_PATH} declares law {law_id!r} and this gate implements no measurement "
            "for it; a declared law nobody evaluates is prose"
        )
    for law_id in sorted(set(findings) - set(titles)):
        raise ClassificationError(
            f"this gate measures {law_id!r} and {BOUNDARY_PATH} declares no such law; a "
            "measurement no declaration claims is a verdict attributable to nothing"
        )

    census: dict[str, int] = {}
    for rule in ordered_rules(boundary):
        census[str(rule.get("class", ""))] = 0
    for result in results:
        if result.status == CLASSIFIED:
            census[result.mutation_class] = census.get(result.mutation_class, 0) + 1
    unresolved_count = sum(1 for r in results if r.status == UNRESOLVED)

    laws = [
        {
            "law_id": law_id,
            "title": titles[law_id],
            "holds": not findings[law_id],
            "violations": findings[law_id],
        }
        for law_id in sorted(titles)
    ]
    return {
        "artifact_id": "EX-018",
        "register": BOUNDARY_PATH,
        "authority": "NONE — DERIVED TRUTH",
        "laws": laws,
        "census": census,
        "subjects": len(results),
        "unresolved": unresolved_count,
        "verdict": "OPEN" if all(law["holds"] for law in laws) else "CLOSED",
    }


def render(report: dict) -> str:
    lines = [
        "EX-018 MUTATION GOVERNANCE BOUNDARY — decidability gate",
        "-" * 78,
        f"  register  : {report['register']}",
        f"  authority : {report['authority']}",
        f"  subjects  : {report['subjects']}",
        "-" * 78,
    ]
    for mutation_class, count in sorted(report["census"].items(), key=lambda kv: (-kv[1], kv[0])):
        lines.append(f"  {count:>6}  {mutation_class}")
    lines.append(
        f"  {report['unresolved']:>6}  UNRESOLVED  (fail-closed terminal — reported, not refused;"
        " it confers no authority)"
    )
    lines.append("-" * 78)
    for law in report["laws"]:
        lines.append(f"  {'ok ' if law['holds'] else 'REFUSED'}  {law['law_id']}  {law['title']}")
        for violation in law["violations"]:
            lines.append(f"          {violation}")
    lines.append("-" * 78)
    lines.append(f"  verdict: {report['verdict']}")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="python -m platform.repository_intelligence.mutation_gate",
        description=(
            "Mutation governance boundary — measure that every declared classification rule "
            "is implemented, reachable, and actually claims subjects."
        ),
    )
    parser.add_argument("--gate", action="store_true", help="exit non-zero when a law refuses")
    parser.add_argument("--repository", default=None, help="repository root to measure")
    parser.add_argument("--json", action="store_true", help="emit the full report as JSON")
    parser.add_argument("--quiet", action="store_true", help="suppress the report when OPEN")
    args = parser.parse_args(argv)

    try:
        report = measure(args.repository)
    except ClassificationError as exc:
        # A FAULT, never a verdict. An unreadable register means no law was measured, which is
        # a different answer from "every law was measured and one refused".
        print(f"FAULT: {exc}", file=sys.stderr)
        return EXIT_FAULT

    closed = report["verdict"] != "OPEN"
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    elif not (args.quiet and not closed):
        print(render(report))
    return EXIT_CLOSED if (closed and args.gate) else EXIT_OPEN


if __name__ == "__main__":  # pragma: no cover - exercised through main()
    raise SystemExit(main())
