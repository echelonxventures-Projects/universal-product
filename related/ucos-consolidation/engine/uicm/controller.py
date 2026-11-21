"""UCOS-UICM-000001 — the closure lifecycle controller and command surface.

One entry point runs the whole lifecycle in the only order that is sound:

    load declaration        the standard being applied, digested
        -> load owners      the three canonical owners, read never written
        -> discover         the population, derived by rule from the boundary
        -> register          one obligation per capability x dimension coordinate
        -> measure           seventeen probes over actual repository state
        -> observe           every transition appended as an immutable observation
        -> project matrix    the grid, a view over the current observations
        -> register gaps     one receipt per non-pass cell
        -> validate          eighteen invariants over the run's own artifacts
        -> project cert      hand the measurement to the located certifier

The order is not stylistic. Obligations precede measurement because a measurement nobody
owed is a finding with no owner. Gaps are derived after measurement because a gap is a
receipt for a cell, not an input to it. Validation runs last over everything else, because
its job is to measure the measurement — and the certification projection runs after
validation because the certifier consumes the validation verdict.

Determinism is established by *doing it twice*. ``--replay`` runs the whole pipeline a
second time in a separate pass and compares matrix digests, and UICM-INV-13 is VIOLATED
rather than skipped when no second measurement exists: determinism nobody re-measured is
not determinism that holds.

Nothing here reads a clock, a commit identity or the working tree's status, and every
emitted byte is a pure function of the declaration plus tracked content. That is what lets
``--replay`` compare bytes rather than parsed structures — a projection that only matches
after normalization is a projection whose canonical form nobody is holding to.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from engine.foundation.contracts.contract import Contract, ContractRegistry, Version
from engine.uicm import gap as gap_module
from engine.uicm import obligation as obligation_module
from engine.uicm.certification import ClosureCertification, project_certification
from engine.uicm.gap import GapRegister
from engine.uicm.matrix import CanonicalOwners, ClosureMatrix, discover_population
from engine.uicm.measurement import RepositoryFacts, measure
from engine.uicm.model import ClosureDeclaration, ClosureError, digest
from engine.uicm.obligation import ObligationRegister
from engine.uicm.observation import ObservationRegistry, build_registry
from engine.uicm.validation import ClosureValidation, validate

#: The programme's operational home, relative to the repository root. Declared here as the
#: single location the controller resolves; the declaration inside it owns everything else.
PROGRAMME_HOME = "00-MASTER/UCOS-UICM-000001"

#: The published capability contract, so the closure measurement is discoverable through
#: the same mechanism every other engine facade uses.
CLOSURE_CONTRACT = Contract(
    name="uicm.closure",
    version=Version(1, 0, 0),
    description=(
        "Measure capability x dimension implementation closure over the discovered "
        "population, register obligations and gaps, and project the measurement to the "
        "located certification owner. Measurement only: owns no registry of identity, "
        "capability, artifact, evidence or certification."
    ),
)

#: Exit codes. ``1`` and ``2`` are deliberately different answers: a refused obligation is
#: not the same event as an inability to reach any verdict at all.
EXIT_OK = 0
EXIT_CLOSED = 1
EXIT_FAULT = 2


def repository_root() -> Path:
    """The repository root, derived from this module's own location."""
    return Path(__file__).resolve().parents[2]


@dataclass(frozen=True, slots=True)
class ClosureRun:
    """One complete, immutable closure lifecycle result."""

    declaration: ClosureDeclaration
    owners: CanonicalOwners
    obligations: ObligationRegister
    observations: ObservationRegistry
    matrix: ClosureMatrix
    gaps: GapRegister
    validation: ClosureValidation
    certification: ClosureCertification | None
    facts: RepositoryFacts

    @property
    def accepted(self) -> bool:
        """True iff every blocking closure invariant holds.

        This is the gate verdict, and it is deliberately *not* "every capability is
        closed". The invariants assert that the measurement is honest — total, evidenced,
        gap-complete, append-only, non-duplicating. Whether the population is closed is a
        separate question the matrix answers, and conflating the two would make the gate
        unable to distinguish a broken measurement from an unfinished repository.
        """
        return self.validation.accepted

    @property
    def fully_closed(self) -> bool:
        """True iff every cell in the matrix is in a pass state."""
        return not self.matrix.non_pass_cells()

    def summary(self) -> dict[str, Any]:
        counts = self.matrix.state_counts()
        return {
            "programme": self.declaration.programme_id,
            "declaration_digest": self.declaration.digest(),
            "capabilities": len(self.matrix.capabilities),
            "dimensions": len(self.matrix.dimension_ids),
            "cells": self.matrix.cell_count,
            "observations": len(self.observations),
            "obligations": len(self.obligations),
            "gaps": len(self.gaps),
            "state_counts": counts,
            "gap_classes": self.gaps.by_class(),
            "invariants": self.validation.counts(),
            "blocking_failures": list(self.validation.blocking_failures),
            "accepted": self.accepted,
            "fully_closed": self.fully_closed,
            "matrix_digest": self.matrix.digest(),
            "observation_head": self.observations.head_hash,
            "obligation_head": self.obligations.head_hash,
            "certification_status": (
                self.certification.status if self.certification else "NOT-PROJECTED"
            ),
        }

    def digest(self) -> str:
        return digest(self.summary())


class UicmController:
    """Executes the closure lifecycle. Holds no state between runs."""

    __slots__ = ("_home", "_repo")

    def __init__(self, repo: Path | None = None, home: Path | None = None) -> None:
        self._repo = Path(repo) if repo is not None else repository_root()
        self._home = Path(home) if home is not None else self._repo / PROGRAMME_HOME

    @property
    def repo(self) -> Path:
        return self._repo

    @property
    def home(self) -> Path:
        return self._home

    def contract(self) -> Contract:
        return CLOSURE_CONTRACT

    def register_contract(self, registry: ContractRegistry) -> None:
        """Publish the closure contract through the located contract registry."""
        registry.register(CLOSURE_CONTRACT)

    def run(self, *, certify: bool = True, replay_digest: str | None = None) -> ClosureRun:
        """Execute the full lifecycle once."""
        declaration = ClosureDeclaration.load(self._home)
        owners = CanonicalOwners.load(self._repo, declaration)
        capabilities = discover_population(self._repo, declaration, owners)
        obligations = obligation_module.build_register(declaration, capabilities)
        findings, facts = measure(self._repo, declaration, owners, capabilities)
        observations = build_registry(capabilities, declaration.dimensions, findings)
        matrix = ClosureMatrix.project(
            declaration=declaration,
            capabilities=capabilities,
            observations=observations,
            source_digests=owners.source_digests(),
        )
        gaps = gap_module.build_register(
            matrix.cells, declaration, obligations, capabilities, self._repo
        )
        validation = validate(
            declaration=declaration,
            matrix=matrix,
            obligations=obligations,
            gaps=gaps,
            owners=owners,
            observations=observations,
            package_root=Path(__file__).resolve().parent,
            replay_digest=replay_digest,
        )
        certification = (
            project_certification(
                declaration=declaration,
                matrix=matrix,
                gaps=gaps,
                validation=validation,
                observations=observations,
            )
            if certify
            else None
        )
        return ClosureRun(
            declaration=declaration,
            owners=owners,
            obligations=obligations,
            observations=observations,
            matrix=matrix,
            gaps=gaps,
            validation=validation,
            certification=certification,
            facts=facts,
        )

    def measure_twice(self) -> tuple[ClosureRun, str]:
        """Run the pipeline twice and return the second run plus the first matrix digest.

        Determinism is established by re-measuring, not by asserting purity. The second run
        carries the first run's digest so UICM-INV-13 has something to compare against.
        """
        first = self.run(certify=False)
        second = self.run(certify=True, replay_digest=first.matrix.digest())
        return second, first.matrix.digest()

    def render(self, run: ClosureRun) -> dict[str, bool]:
        """Write the declared record set. Returns artifact name -> bytes changed."""
        written: dict[str, bool] = {}
        for name, text in _record_set(run).items():
            written[name] = _write_text(self._home / name, text)
        return written

    def replay(self, run: ClosureRun) -> tuple[bool, tuple[str, ...]]:
        """Re-render in memory and compare committed bytes. Returns (clean, drifted).

        Byte comparison, not parsed comparison. A register that only matches after
        normalization is a register whose canonical form nobody is holding to, and the
        remedy for a drift report is never to edit the file — it is to re-render it from
        the declaration and the tree.
        """
        drifted: list[str] = []
        for name, text in _record_set(run).items():
            path = self._home / name
            try:
                committed = path.read_text(encoding="utf-8")
            except OSError:
                drifted.append(name)
                continue
            if committed != text:
                drifted.append(name)
        return not drifted, tuple(drifted)


# --------------------------------------------------------------------------- #
# The declared record set. Every byte is a function of the declaration and the  #
# tracked tree: no clock, no commit identity, no coverage percentage.           #
# --------------------------------------------------------------------------- #


def _write_text(path: Path, text: str) -> bool:
    """Write only when the bytes differ, so an unchanged run leaves mtime alone."""
    try:
        if path.read_text(encoding="utf-8") == text:
            return False
    except OSError:
        pass
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return True


def _json_document(payload: Mapping[str, Any]) -> str:
    return json.dumps(payload, indent=2, ensure_ascii=False) + "\n"


def _artifact_names(run: ClosureRun) -> dict[str, str]:
    """Renderer name -> artifact filename, read from the declared record set."""
    return {
        str(record["renderer"]): str(record["artifact"])
        for record in run.declaration.section("record_set")
    }


def _record_set(run: ClosureRun) -> dict[str, str]:
    """Render every declared artifact. A declared renderer with no implementation faults."""
    names = _artifact_names(run)
    renderers = {
        "matrix": _render_matrix,
        "obligations": _render_obligations,
        "observations": _render_observations,
        "measurement": _render_measurement,
        "gaps": _render_gaps,
        "certification": _render_certification,
    }
    missing = sorted(set(names) - set(renderers))
    if missing:
        raise ClosureError("declared renderer is not implemented", renderers=missing)
    return {names[renderer]: renderers[renderer](run) for renderer in names}


def _header(run: ClosureRun, title: str, artifact: str) -> list[str]:
    programme = run.declaration.document["programme"]
    return [
        f"# {title}",
        "",
        f"> **Register:** `{artifact}`  ",
        f"> **Programme:** {programme['id']} v{programme['version']}  ",
        "> **AUTHORITY = NONE — DERIVED TRUTH**  ",
        f"> **Role:** {programme['disposition']}  ",
        "> **Producer:** `engine/uicm` — `python -m engine.uicm.controller --render`  ",
        f"> **Declaration digest:** `{run.declaration.digest()[:16]}`  ",
        f"> **Matrix digest:** `{run.matrix.digest()[:16]}`  ",
        "> Determinism: no wall clock, no commit identity, no coverage percentage. This",
        "> file is a projection and never a source; the remedy for drift is to re-render.",
        "",
    ]


def _render_matrix(run: ClosureRun) -> str:
    names = _artifact_names(run)
    lines = _header(
        run,
        "Universal Implementation Closure Matrix",
        names["matrix"],
    )
    summary = run.summary()
    lines += [
        "## Measured population",
        "",
        f"**{summary['capabilities']} capabilities x {summary['dimensions']} dimensions = "
        f"{summary['cells']} measured cells.**",
        "",
        "| Quantity | Value |",
        "|---|---:|",
        f"| Capabilities discovered | {summary['capabilities']} |",
        f"| Closure dimensions declared | {summary['dimensions']} |",
        f"| Measured cells | {summary['cells']} |",
        f"| Observations recorded | {summary['observations']} |",
        f"| Obligations registered | {summary['obligations']} |",
        f"| Gaps registered | {summary['gaps']} |",
        f"| Blocking invariant violations | {len(summary['blocking_failures'])} |",
        "",
        "## Closure state distribution",
        "",
        "| State | Cells |",
        "|---|---:|",
    ]
    for state, count in summary["state_counts"].items():
        lines.append(f"| {state} | {count} |")
    lines += [
        "",
        "## Dimension closure",
        "",
        "| # | Dimension | Question | CLOSED | OPEN | BLOCKED |",
        "|---:|---|---|---:|---:|---:|",
    ]
    counts = run.matrix.dimension_counts()
    for dimension in run.declaration.dimensions:
        row = counts[dimension.id]
        lines.append(
            f"| {dimension.ordinal} | {dimension.name} | {dimension.question} | "
            f"{row['CLOSED']} | {row['OPEN']} | {row['BLOCKED']} |"
        )
    lines += [
        "",
        "## The matrix",
        "",
        "Columns are the declared dimensions in ordinal order. `C` closed, `O` open,",
        "`B` blocked. A row is only as closed as its least closed dimension.",
        "",
        "| Capability | Capability ID | Owner | "
        + " | ".join(str(d.ordinal) for d in run.declaration.dimensions)
        + " | Row |",
        "|---|---|---|" + "---:|" * len(run.declaration.dimensions) + "---|",
    ]
    glyph = {"CLOSED": "C", "OPEN": "O", "BLOCKED": "B"}
    rows = run.matrix.by_capability()
    for capability in run.matrix.capabilities:
        cells = {c.dimension_id: c for c in rows[capability.name]}
        marks = " | ".join(
            glyph.get(cells[d.id].state.value, cells[d.id].state.value[0])
            for d in run.declaration.dimensions
        )
        lines.append(
            f"| `{capability.name}` | `{capability.capability_id}` | "
            f"{capability.canonical_owner} | {marks} | "
            f"**{run.matrix.capability_state(capability.name).value}** |"
        )
    lines += [
        "",
        "## What this register does not claim",
        "",
        "The matrix measures repository state. It certifies nothing, discharges no gap and",
        "overrides no owner: where a cell and a located instrument disagree, the located",
        "instrument governs and the divergence is a referred finding. Capability identity",
        "is read from the capability register, artifact identity from UCOS-UGA-001, and",
        "implementation status from the RIE catalogue — UICM mints none of them.",
        "",
    ]
    return "\n".join(lines)


def _render_obligations(run: ClosureRun) -> str:
    return _json_document(run.obligations.to_document())


def _render_observations(run: ClosureRun) -> str:
    return _json_document(run.observations.to_document())


def _render_measurement(run: ClosureRun) -> str:
    document = run.matrix.to_document()
    document["validation"] = run.validation.to_document()
    document["summary"] = run.summary()
    return _json_document(document)


def _render_gaps(run: ClosureRun) -> str:
    document = run.gaps.to_document()
    document["classification_reference"] = dict(
        gap_module.classification_reference(run.declaration)
    )
    return _json_document(document)


def _render_certification(run: ClosureRun) -> str:
    names = _artifact_names(run)
    lines = _header(run, "Closure Certification", names["certification"])
    binding = run.declaration.section("certification_binding")
    lines += [
        "## Role",
        "",
        f"UICM is a **{binding['binding']}**, not a certification authority. The verdict",
        f"below is the decision of `{binding['owner']}` ({binding['owner_id']}), reported",
        "unchanged. UICM supplies three inputs and has no code path that can upgrade,",
        "retry or reinterpret a refusal.",
        "",
    ]
    if run.certification is None:
        lines += ["## Verdict", "", "Certification was not projected in this run.", ""]
        return "\n".join(lines)
    certification = run.certification
    lines += [
        "## Verdict",
        "",
        "| Field | Value |",
        "|---|---|",
        f"| Status | **{certification.status}** |",
        f"| Certification id | `{certification.certification_id}` |",
        f"| Certification owner | `{binding['owner']}` |",
        f"| Blocking rule failures | {len(certification.blocking_failures)} |",
        f"| Evidence sha256 | `{certification.evidence.content_sha256()[:32]}` |",
        "",
        "## Submitted measurements",
        "",
        "Every verdict below is *computed* from the value and threshold by the located",
        "engine, never asserted by UICM.",
        "",
        "| Metric | Value | Threshold | Satisfied |",
        "|---|---:|---:|---|",
    ]
    for measurement in certification.measurement_input.measurements:
        lines.append(
            f"| `{measurement.metric_id}` | {measurement.value:g} | "
            f"{measurement.threshold:g} | {'yes' if measurement.satisfied else 'NO'} |"
        )
    lines += [
        "",
        "## Rule findings",
        "",
        "| Rule | Status |",
        "|---|---|",
    ]
    for finding in certification.decision.findings:
        lines.append(f"| `{finding.rule_id}` | {finding.status.value} |")
    lines += [
        "",
        "## Closure invariants",
        "",
        "| Invariant | Name | Verdict |",
        "|---|---|---|",
    ]
    for result in run.validation.results:
        lines.append(f"| `{result.invariant_id}` | {result.name} | {result.verdict} |")
    lines += [
        "",
        "## Reading this verdict",
        "",
        f"The population carries **{len(run.gaps)} registered gap(s)** across",
        f"{len(run.matrix.non_pass_cells())} non-pass cell(s), so the closure metric",
        "falls short of total closure and the located engine refuses accordingly. That",
        "refusal is the correct measurement of the current repository, not a defect in",
        "the measurement: certifying closure over an unclosed population is precisely the",
        "unverified claim this programme exists to refuse.",
        "",
    ]
    return "\n".join(lines)


def _emit(text: str, *, quiet: bool) -> None:
    if not quiet:
        print(text)


def _report(run: ClosureRun, *, quiet: bool) -> None:
    summary = run.summary()
    _emit(
        f"UICM {summary['programme']} — {summary['capabilities']} capabilities x "
        f"{summary['dimensions']} dimensions = {summary['cells']} measured cells",
        quiet=quiet,
    )
    _emit(
        "  states: " + ", ".join(f"{k}={v}" for k, v in summary["state_counts"].items() if v),
        quiet=quiet,
    )
    _emit(
        f"  observations={summary['observations']} obligations={summary['obligations']} "
        f"gaps={summary['gaps']}",
        quiet=quiet,
    )
    _emit(
        f"  invariants: {summary['invariants']['satisfied']}/"
        f"{summary['invariants']['total']} satisfied",
        quiet=quiet,
    )
    for result in run.validation.results:
        if not result.satisfied:
            _emit(f"    {result.invariant_id} {result.name}: {result.detail}", quiet=quiet)
    _emit(f"  matrix digest: {summary['matrix_digest']}", quiet=quiet)
    _emit(f"  certification: {summary['certification_status']}", quiet=quiet)


def main(argv: list[str] | None = None) -> int:
    """The command surface. Exit 1 means an obligation was refused; 2 means no verdict."""
    parser = argparse.ArgumentParser(
        prog="ucos-uicm",
        description="Universal Implementation Closure Matrix — measurement and certification.",
    )
    parser.add_argument(
        "--matrix", action="store_true", help="measure and report the closure matrix"
    )
    parser.add_argument(
        "--closure", action="store_true", help="fail-closed closure validation gate"
    )
    parser.add_argument("--render", action="store_true", help="write the declared record set")
    parser.add_argument(
        "--replay", action="store_true", help="assert the committed record set reproduces"
    )
    parser.add_argument("--quiet", action="store_true", help="suppress narrative output")
    args = parser.parse_args(argv)

    if not any((args.matrix, args.closure, args.render, args.replay)):
        parser.print_help()
        return EXIT_OK

    controller = UicmController()
    try:
        run, first_digest = controller.measure_twice()
    except ClosureError as exc:
        print(f"UICM FAULT: {exc}", file=sys.stderr)
        return EXIT_FAULT

    if args.matrix or args.closure:
        _report(run, quiet=args.quiet)
        _emit(f"  replay digest: {first_digest}", quiet=args.quiet)

    status = EXIT_OK

    if args.render:
        changed = controller.render(run)
        for name, altered in sorted(changed.items()):
            _emit(f"  {'wrote' if altered else 'unchanged'} {name}", quiet=args.quiet)

    if args.replay:
        clean, drifted = controller.replay(run)
        if not clean:
            for name in drifted:
                print(f"UICM REPLAY DRIFT: {name}", file=sys.stderr)
            status = EXIT_CLOSED
        else:
            _emit("  replay: no drift", quiet=args.quiet)

    if args.closure and not run.accepted:
        for invariant_id in run.validation.blocking_failures:
            result = run.validation.result(invariant_id)
            print(
                f"UICM CLOSURE REFUSED: {invariant_id} {result.name} — {result.detail}",
                file=sys.stderr,
            )
        return EXIT_CLOSED

    if args.closure and status == EXIT_OK:
        _emit("UICM closure validation passed.", quiet=args.quiet)

    return status


if __name__ == "__main__":  # pragma: no cover - module CLI entry
    raise SystemExit(main())


__all__ = [
    "CLOSURE_CONTRACT",
    "EXIT_CLOSED",
    "EXIT_FAULT",
    "EXIT_OK",
    "PROGRAMME_HOME",
    "ClosureRun",
    "UicmController",
    "main",
    "repository_root",
]
