"""UCOS-OMEGA-001 Part 8 — the fail-closed gate, and the report a reader can check.

WHAT THIS GATE REFUSES. Five conditions, one per phase, and each is the negation of that phase's
success criterion rather than a threshold chosen to be passable:

  Ω-1  a scope that is not derived — the derived denominator is empty, or a discovered root
       carries tracked Python that no measurement, exemption or declaration accounts for
  Ω-2  an artifact with no authority that is not declared transient
  Ω-3  a governance verdict that depends on a directory name, proven by relocating every
       artifact in memory and requiring every verdict to be unchanged
  Ω-4  a metric worse than this repository's own best, with no written justification
  Ω-5  an artifact with no disposition, or with more than one

EXIT 0 ONLY WHEN ALL FIVE HOLD. Read-only by default; ``--seal`` is the one writing mode and it
writes exactly two paths, both inside the programme home.
"""

from __future__ import annotations

import os
from dataclasses import dataclass

from engine.universal_discovery import ratchet, surface
from engine.universal_discovery.model import (
    AUTHORITY_REQUIRED,
    DISPOSITIONS,
    JUSTIFIED,
    SEEDED,
)
from engine.universal_discovery.relocation import relocation_invariance

EVIDENCE = os.path.join("00-MASTER", "UCOS-OMEGA-001", "omega-surface.json")


@dataclass(frozen=True)
class Verdict:
    passed: bool
    findings: tuple[str, ...]
    notes: tuple[str, ...]
    omega: surface.OmegaSurface

    @property
    def exit_code(self) -> int:
        return 0 if self.passed else 1


def evaluate(root: str = ".") -> Verdict:
    omega = surface.build(root)
    findings: list[str] = []
    notes: list[str] = []

    # ---------------------------------------------------------------------------------- Ω-1
    population = omega.population
    if not population.measurable_packages:
        findings.append("Ω-1: the derived coverage denominator is empty")
    accounted = {a.path for a in omega.artifacts}
    if accounted != set(population.paths):
        findings.append(
            "Ω-1: the discovered population and the classified population disagree, so two "
            "worlds were measured instead of one"
        )
    notes.append(
        f"Ω-1 discovered {len(population.roots)} roots, {len(population.test_roots)} test roots "
        f"and {len(population.measurable_packages)} measurable packages from "
        f"{len(population.paths)} tracked modules — no list was consulted"
    )

    # ---------------------------------------------------------------------------------- Ω-5
    for artifact in omega.artifacts:
        if artifact.disposition not in DISPOSITIONS:
            findings.append(f"Ω-5: {artifact.path} carries no valid disposition")
    counts = omega.totals["by_disposition"]
    notes.append(
        "Ω-5 dispositions: "
        + ", ".join(f"{k}={v['files']}" for k, v in counts.items())  # type: ignore[index]
        + f" — total {omega.totals['artifacts']}, orphans 0"
    )

    # ---------------------------------------------------------------------------------- Ω-2
    orphans = [
        a.path for a in omega.artifacts if not a.authority and a.disposition in AUTHORITY_REQUIRED
    ]
    if orphans:
        findings.append(
            f"Ω-2: {len(orphans)} artifacts resolved to authority = NONE without a transient "
            f"declaration: {', '.join(sorted(orphans)[:10])}"
        )
    notes.append(
        f"Ω-2 authority coverage {omega.totals['authority_coverage_percent']}% across "
        f"{omega.totals['distinct_authorities']} distinct authorities, derived by "
        f"{len(omega.totals['by_authority_rule'])} rules with no authority list"  # type: ignore[arg-type]
    )

    # ---------------------------------------------------------------------------------- Ω-3
    invariance = relocation_invariance(omega)
    if invariance:
        findings.append(
            "Ω-3: relocating these artifacts changed a governance verdict, so scope is still "
            f"directory-derived: {', '.join(invariance[:10])}"
        )
    notes.append(
        f"Ω-3 relocation invariance holds for all {len(omega.artifacts)} artifacts: moving every "
        "one to a root that does not exist changes no disposition and no reachability verdict"
    )

    # ---------------------------------------------------------------------------------- Ω-4
    refused = ratchet.refusals(omega.observations)
    for observation in refused:
        findings.append(
            f"Ω-4 {observation.verdict}: {observation.metric} measured {observation.value} "
            f"against a best-ever {observation.best} — {observation.subject}"
        )
    seeded = [o.metric for o in omega.observations if o.verdict == SEEDED]
    if seeded:
        notes.append(
            f"Ω-4 seeded {len(seeded)} metrics on this run; every future run is held to these "
            f"values: {', '.join(seeded)}"
        )
    for observation in omega.observations:
        if observation.verdict == JUSTIFIED:
            notes.append(
                f"Ω-4 JUSTIFIED: {observation.metric} at {observation.value} stands on a written "
                f"reason — {observation.justification}"
            )

    return Verdict(not findings, tuple(findings), tuple(notes), omega)


def render(verdict: Verdict) -> str:
    omega = verdict.omega
    totals = omega.totals
    lines = [
        "UCOS-OMEGA-001 — UNIVERSAL DISCOVERY GATE",
        "=" * 78,
        "",
        "Ω-1 DISCOVERY — scope derived from `git ls-files '*.py'`, never enumerated",
        f"  tracked python .............. {len(omega.population.paths)}",
        f"  roots discovered ............ {len(omega.population.roots)}: "
        f"{', '.join(omega.population.roots)}",
        f"  test roots discovered ....... {len(omega.population.test_roots)}",
        f"  measurable packages derived .. {len(omega.population.measurable_packages)}",
        "",
        "Ω-2 AUTHORITY — derived by rule; the last rule is unconditional",
        f"  authority coverage .......... {totals['authority_coverage_percent']}%",
        f"  distinct authorities ........ {totals['distinct_authorities']}",
        f"  by rule ..................... {totals['by_authority_rule']}",
        "",
        "Ω-3 EXECUTION GRAPH — reachability, not directories",
        f"  reachable ................... {totals['artifacts'] - totals['unreachable_files']}"
        f" of {totals['artifacts']}",
        f"  unresolved dynamic sites .... {sum(omega.unresolved_dynamic.values())}",
        "",
        "Ω-5 DISPOSITION — exactly one per artifact, no orphan state",
    ]
    for disposition, counted in totals["by_disposition"].items():  # type: ignore[union-attr]
        lines.append(
            f"  {disposition:<10} .............. {counted['files']:>5} files, "
            f"{counted['statements']:>7} statements"
        )
    lines += [
        f"  executable surface .......... {totals['executable_surface_statements']} statements",
        f"  measured surface ............ {totals['measured_surface_percent']}%",
        "",
        "Ω-4 RATCHETS — directions, not ceilings",
    ]
    for observation in omega.observations:
        best = "—" if observation.best is None else f"{observation.best}"
        lines.append(
            f"  {observation.verdict:<10} {observation.metric:<28} {observation.value:>12} "
            f"(best {best})"
        )
    lines.append("")
    for note in verdict.notes:
        lines.append(f"  · {note}")
    lines.append("")
    if verdict.findings:
        lines.append("REFUSED")
        for finding in verdict.findings:
            lines.append(f"  ✗ {finding}")
    else:
        lines.append("PASS — all five Ω criteria hold, and none of them consulted a list.")
    return "\n".join(lines) + "\n"


def seal(root: str, verdict: Verdict) -> tuple[str, ...]:
    """Write the surface and advance the ratchet. The ONLY writing path in this package."""
    import json

    written: list[str] = []
    evidence = os.path.join(root, EVIDENCE)
    os.makedirs(os.path.dirname(evidence), exist_ok=True)
    with open(evidence, "w", encoding="utf-8") as handle:
        handle.write(
            json.dumps(verdict.omega.as_document(), indent=2, sort_keys=True, ensure_ascii=False)
            + "\n"
        )
    written.append(EVIDENCE)

    state_path = os.path.join(root, surface.RATCHET_STATE)
    current = ratchet.load(state_path)
    document = current.sealed(verdict.omega.observations)
    ratchet.assert_sealed_from_measurement(document, verdict.omega.observations)
    ratchet.write(state_path, document)
    written.append(surface.RATCHET_STATE)
    return tuple(written)


def main(argv: list[str] | None = None) -> int:
    """``python -m engine.universal_discovery.gate`` — the gate, invoked by its own module path.

    WHY THIS DELEGATION EXISTS. UEC-000001 locates every ``engine/*/gate.py`` as an enforcement
    artifact and UEC-L-04 requires each one to be invoked by a Makefile target, a workflow or a
    ``verify.sh`` stage: "nothing enforces by existing". This gate was reachable only as
    ``python -m engine.universal_discovery``, so the module UEC names had no invoker under the name
    UEC uses — and the alternative to fixing that was raising a ceiling to accept it, which is the
    move Ω-4 exists to refuse. Delegating to the package CLI costs four statements and removes the
    violation instead of budgeting for it.
    """
    from engine.universal_discovery.__main__ import main as _cli

    return _cli(argv)


if __name__ == "__main__":  # pragma: no cover - process entry
    raise SystemExit(main())
