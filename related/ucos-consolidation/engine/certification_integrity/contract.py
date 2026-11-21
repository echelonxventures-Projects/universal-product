"""UCI-000001 Part 9 — the laws, and the gate's arithmetic.

WHAT A LAW IS HERE. A named question with a measured answer and no discretion in between. Each
law returns the OFFENDING IDENTITIES rather than a count, so a refusal names its subject instead
of its size — the same construction ``engine/enforcement_closure/contract.py`` uses and for the
same reason recorded there: "18 engines are untested" is not actionable and a list of eighteen
paths is.

EVERY LAW BLOCKS. There is no ``blocking: false``. A law that could be switched off is not a law,
and the switch would be reachable by exactly the mutation the law detects. UEC-000001 makes the
same choice and enforces it at load time; here it is structural, because there is no field to set.

THE RATCHET IS TWO-SIDED, AND THAT IS THE ONLY HONEST FORM.

Every counted law reads its ceiling from ``uci-declaration.json``. Above the ceiling is a refusal:
new debt. BELOW the ceiling is also a refusal: debt was repaid and the ceiling was not tightened,
so the declaration is carrying slack a future regression could occupy in silence. The satisfied
state is equality, exactly. Rule 1 of the mandate forbids raising a ceiling without justification;
this construction additionally forbids leaving one loose, which is the failure mode that lets a
ratchet drift into decoration.

WHAT THIS MODULE REFUSES TO DO. It does not compute a coverage percentage and compare it to a
threshold. ``pyproject.toml`` already owns the floor and ``verify.sh`` already applies it once over
the combined data. A second opinion about the same number, held in a second place, is how the
denominator came to be declared twice.
"""

from __future__ import annotations

import json
import os
from collections.abc import Callable, Mapping
from dataclasses import dataclass, field

from engine.certification_integrity import inventory as inventory_module
from engine.certification_integrity.model import (
    FILE_EXECUTABLE,
    FILE_TOOLING,
    IntegrityError,
)
from engine.universal_discovery import ratchet as omega_ratchet
from engine.universal_discovery.model import RATCHET_KINDS

DECLARATION_RELATIVE = "00-MASTER/UCI-000001/uci-declaration.json"

OPEN = "OPEN"
CLOSED = "CLOSED"
FAULT = "FAULT"

HOLDS = "HOLDS"
REFUSED = "REFUSED"


@dataclass(frozen=True)
class Law:
    """One declared law: an id, the question, and the measurement bound to it."""

    law_id: str
    name: str
    question: str


@dataclass
class LawResult:
    law_id: str
    name: str
    question: str
    status: str
    measured: int
    ceiling: int | None
    offenders: tuple[str, ...]
    detail: str

    @property
    def holds(self) -> bool:
        return self.status == HOLDS

    def as_record(self) -> dict[str, object]:
        return {
            "law": self.law_id,
            "name": self.name,
            "question": self.question,
            "status": self.status,
            "measured": self.measured,
            "ceiling": self.ceiling,
            "offenders": list(self.offenders[:32]),
            "offender_total": len(self.offenders),
            "detail": self.detail,
        }


@dataclass
class Declaration:
    """The governed expectation. Data, so that changing it is a reviewable diff.

    ``ratchet`` USED TO HOLD SIX NUMBERS and now holds six KINDS. The numbers were 65, 27, 39, 25,
    14 and 10, and two of them had been 607 and 570 a week earlier — measurements taken on the
    afternoon somebody took them, carried in a file that needed a changelog to explain itself. A
    threshold that needs a changelog is a diary, not a threshold.

    Ω-4 replaces the number with a DIRECTION. What the declaration now states per law is which
    direction is better and how strictly, and the value each run is held to is this repository's
    own best-ever measurement, sealed by ``--seal`` from a measurement rather than typed.
    """

    version: str
    ratchet: Mapping[str, str]
    source: str
    raw: Mapping[str, object] = field(default_factory=dict)


def load_declaration(root: str) -> Declaration:
    path = os.path.join(root, DECLARATION_RELATIVE)
    if not os.path.exists(path):
        raise IntegrityError(
            f"{DECLARATION_RELATIVE} is absent, so there is no governed expectation to measure "
            "against. A gate with no declaration cannot refuse anything and is not run."
        )
    try:
        with open(path, encoding="utf-8") as handle:
            document = json.load(handle)
    except (OSError, json.JSONDecodeError) as exc:
        raise IntegrityError(f"{DECLARATION_RELATIVE} is unparseable: {exc}") from exc
    ratchet = {
        key: value
        for key, value in (document.get("ratchet") or {}).items()
        if not key.startswith("$")
    }
    for key, value in ratchet.items():
        if value not in RATCHET_KINDS:
            raise IntegrityError(
                f"ratchet.{key} is {value!r}; under Ω-4 a ratchet declares its KIND — one of "
                f"{', '.join(RATCHET_KINDS)} — and never a numeric ceiling. A number here would be "
                "a historical snapshot that a repository of any other size has to rewrite."
            )
    return Declaration(
        version=str(document.get("version", "0")),
        ratchet=ratchet,
        source=DECLARATION_RELATIVE,
        raw=document,
    )


# ------------------------------------------------------------------------------ measurements
# Each returns the offending identities. Sorted, so a diff of two runs is a diff of findings and
# not of iteration order.


def executable_outside_denominator(inv: inventory_module.Inventory) -> list[str]:
    """Rule 2's refusal: an executable artifact the coverage denominator does not contain."""
    return sorted(inv.executable_outside_denominator)


def ungoverned_executables(inv: inventory_module.Inventory) -> list[str]:
    """Rule 3's refusal: a file no authority anywhere claims."""
    return sorted(inv.ungoverned_files)


def unmeasured_governance_engines(inv: inventory_module.Inventory) -> list[str]:
    """Governance engines outside the denominator.

    Separated from ``executable_outside_denominator`` even though it is a subset, because the two
    have different remedies and very different severity: an unmeasured helper is coverage debt, an
    unmeasured GATE is a protection whose executed fraction is unknown and which can therefore
    have rotted into a no-op while still reporting OPEN.
    """
    return sorted(
        record.path
        for record in inv.files
        if not record.measured and record.governing_authority.startswith("UEC-000001")
    )


def engines_without_tests(inv: inventory_module.Inventory) -> list[str]:
    """Rule 5: an engine no test module references."""
    return sorted(
        record.path
        for record in inv.files
        if record.governing_authority.startswith("UEC-000001")
        and "test" not in record.invocation_sources
    )


def single_plane_engines(inv: inventory_module.Inventory) -> list[str]:
    """Rule 6, measured over plane TYPES rather than invoking texts."""
    return sorted(
        record.path
        for record in inv.files
        if record.governing_authority.startswith("UEC-000001")
        and len([p for p in record.invocation_sources if p != "test"]) < 2
    )


def files_with_no_execution_path(inv: inventory_module.Inventory) -> list[str]:
    """A measured file with statements and no callable of its own that any test could enter.

    Not the same as uncovered. A module of pure top-level assignments has no execution path and can
    still be 100% covered by being imported, which is how import-only coverage inflates a figure
    without exercising behaviour.
    """
    return sorted(
        record.path
        for record in inv.files
        if record.measured
        and record.ast_statements > 20
        and not record.execution_paths
        and record.classification in (FILE_EXECUTABLE, FILE_TOOLING)
    )


#: key -> (law id, measurement). Registering the pair in one table is what keeps a measurement
#: from existing with no law and a law from existing with no measurement.
RATCHETED: Mapping[str, tuple[str, Callable[[inventory_module.Inventory], list[str]]]] = {
    "executable_outside_denominator": ("UCI-L-01", executable_outside_denominator),
    "ungoverned_executables": ("UCI-L-02", ungoverned_executables),
    "unmeasured_governance_engines": ("UCI-L-03", unmeasured_governance_engines),
    "engines_without_tests": ("UCI-L-04", engines_without_tests),
    "single_plane_engines": ("UCI-L-05", single_plane_engines),
    "files_with_no_execution_path": ("UCI-L-06", files_with_no_execution_path),
}

LAWS: Mapping[str, Law] = {
    "UCI-L-01": Law(
        "UCI-L-01",
        "coverage_scope_equals_executable_scope",
        "is every executable artifact inside the measured denominator? (Rule 2)",
    ),
    "UCI-L-02": Law(
        "UCI-L-02",
        "every_file_has_a_governing_authority",
        "does some authority claim every tracked Python artifact? (Rule 3)",
    ),
    "UCI-L-03": Law(
        "UCI-L-03",
        "governance_engines_are_measured",
        "is every enforcement engine's executed fraction known? (Rule 2/5)",
    ),
    "UCI-L-04": Law(
        "UCI-L-04",
        "every_engine_has_a_test",
        "does a test module reference every governance engine? (Rule 5)",
    ),
    "UCI-L-05": Law(
        "UCI-L-05",
        "every_engine_has_two_invocation_planes",
        "is every engine reachable from at least two plane TYPES? (Rule 6)",
    ),
    "UCI-L-06": Law(
        "UCI-L-06",
        "measured_files_have_execution_paths",
        "does every substantial measured file expose a callable a test could enter?",
    ),
}


#: Where UCI's own best-ever values are sealed. Inside the programme home, so Ω-A-03 assigns its
#: authority by the same ancestry rule as every other programme artifact.
RATCHET_STATE_RELATIVE = os.path.join("00-MASTER", "UCI-000001", "uci-ratchet.json")


def _ratcheted(
    inv: inventory_module.Inventory,
    declaration: Declaration,
    key: str,
    state: omega_ratchet.Ratchet,
) -> LawResult:
    """Compare one measurement against this repository's own best, not against a chosen number.

    THE FOUR OUTCOMES, and why only two of them refuse:

      IMPROVED / SEEDED  the measurement is better than anything recorded, or is the first
                         recording. HOLDS, and no file needs editing to permit it. Under the
                         previous two-sided ceiling this was a REFUSAL — repaying debt failed the
                         gate until somebody committed the new number, which is how a mechanism
                         meant to prevent regression became a tax on improvement. It failed exactly
                         that way on the commit that introduced Ω: the denominator improved 65→64
                         and the gate closed.
      HELD               equal to the best. HOLDS.
      JUSTIFIED          worse, and the sealed state names this key with a written reason. HOLDS,
                         and the reason is visible in a diff forever. ``best`` does NOT move, so
                         the repository is still held to what it once achieved.
      REGRESSED/STALLED  worse with no reason, or a CONVERGENT metric that has stopped falling.
                         REFUSED.
    """
    law_id, measurement = RATCHETED[key]
    law = LAWS[law_id]
    offenders = tuple(measurement(inv))
    measured = len(offenders)
    kind = declaration.ratchet.get(key)

    if kind is None:
        return LawResult(
            law_id=law_id,
            name=law.name,
            question=law.question,
            status=REFUSED,
            measured=measured,
            ceiling=None,
            offenders=offenders,
            detail=(
                f"ratchet.{key} declares no KIND, so this measurement is recorded and enforced by "
                f"nothing. Declare it in {DECLARATION_RELATIVE} as one of "
                f"{', '.join(RATCHET_KINDS)}."
            ),
        )

    observation = state.observe(key, kind, float(measured), law.question)
    best = None if observation.best is None else int(observation.best)

    if observation.refused:
        detail = (
            f"{observation.verdict}: measured {measured} against a best-ever {best}. "
            f"{measured - (best or 0)} unit(s) of new debt. First offenders: "
            f"{', '.join(offenders[:8])}"
            if observation.verdict == omega_ratchet.REGRESSED
            else (
                f"STALLED: a CONVERGENT ratchet has held at {measured} for "
                f"{omega_ratchet.STALL_OBSERVATIONS} runs without falling. Either reduce it, or "
                f"record in {RATCHET_STATE_RELATIVE} justifications why {measured} is its floor."
            )
        )
        return LawResult(
            law_id=law_id,
            name=law.name,
            question=law.question,
            status=REFUSED,
            measured=measured,
            ceiling=best,
            offenders=offenders,
            detail=detail,
        )

    if observation.verdict == omega_ratchet.IMPROVED:
        detail = (
            f"IMPROVED: {best} -> {measured}. Nothing needs editing to permit this; "
            "`make uci-seal` records the new best."
        )
    elif observation.verdict == omega_ratchet.SEEDED:
        detail = (
            f"SEEDED at {measured}. Every future run is held to this value or better, with no "
            "number authored by hand."
        )
    elif observation.verdict == omega_ratchet.JUSTIFIED:
        detail = (
            f"JUSTIFIED: measured {measured} above the best-ever {best} on a written reason — "
            f"{observation.justification}"
        )
    else:
        detail = f"HELD at the best-ever {measured}"

    return LawResult(
        law_id=law_id,
        name=law.name,
        question=law.question,
        status=HOLDS,
        measured=measured,
        ceiling=best,
        offenders=offenders,
        detail=detail,
    )


def measure(root: str, *, coverage_xml: str | None = None) -> dict[str, object]:
    """Measure every law. Returns the report; the caller decides the exit code."""
    declaration = load_declaration(root)
    inv = inventory_module.build(root, coverage_xml=coverage_xml)
    state = omega_ratchet.load(os.path.join(root, RATCHET_STATE_RELATIVE))

    results = [_ratcheted(inv, declaration, key, state) for key in sorted(RATCHETED)]
    refused = [r for r in results if not r.holds]

    declared_keys = set(declaration.ratchet)
    known_keys = set(RATCHETED)
    orphan_ceilings = sorted(declared_keys - known_keys)
    if orphan_ceilings:
        # A ratchet with no measurement is a declaration that looks like enforcement and is not.
        results.append(
            LawResult(
                law_id="UCI-L-07",
                name="every_ceiling_binds_a_measurement",
                question="does every declared ratchet bind a measurement that exists?",
                status=REFUSED,
                measured=len(orphan_ceilings),
                ceiling=0,
                offenders=tuple(orphan_ceilings),
                detail=(
                    "these ratchet keys are declared but measured by nothing: "
                    f"{', '.join(orphan_ceilings)}"
                ),
            )
        )
        refused = [r for r in results if not r.holds]

    return {
        "schema": "ucos-certification-integrity-report",
        "version": "1.0.0",
        "declaration": DECLARATION_RELATIVE,
        "declaration_version": declaration.version,
        "status": CLOSED if refused else OPEN,
        "counts": {
            "laws": len(results),
            "holds": sum(1 for r in results if r.holds),
            "refused": len(refused),
            "files": len(inv.files),
            "objects": len(inv.objects),
        },
        "ratchet_kinds": dict(sorted(declaration.ratchet.items())),
        "ratchet_best": {key: state.best.get(key) for key in sorted(RATCHETED)},
        "ratchet_measured": {
            key: len(measurement(inv)) for key, (_law, measurement) in sorted(RATCHETED.items())
        },
        "totals": inv.totals,
        "scope_drift": inv.scope_drift,
        "coverage_document": _coverage_document(root, coverage_xml),
        "laws": [r.as_record() for r in results],
        "inventory_digest": inv.digest(),
    }


def seal_ratchet(root: str, *, coverage_xml: str | None = None) -> str:
    """Advance UCI's best-ever values from a measurement. The one writing path for the ratchet.

    Sealing is not a way to make a refusal pass: ``sealed`` only ever moves ``best`` DOWNWARD, and
    ``assert_sealed_from_measurement`` refuses a state file looser than the run that wrote it. A
    regression therefore cannot be sealed away — it can only be justified, in writing, and the
    justification never moves the bound.
    """
    declaration = load_declaration(root)
    inv = inventory_module.build(root, coverage_xml=coverage_xml)
    path = os.path.join(root, RATCHET_STATE_RELATIVE)
    state = omega_ratchet.load(path)
    observations = [
        state.observe(
            key,
            declaration.ratchet[key],
            float(len(measurement(inv))),
            LAWS[law].question,
        )
        for key, (law, measurement) in sorted(RATCHETED.items())
        if key in declaration.ratchet
    ]
    document = state.sealed(observations)
    omega_ratchet.assert_sealed_from_measurement(document, observations)
    omega_ratchet.write(path, document)
    return RATCHET_STATE_RELATIVE


def _coverage_document(root: str, coverage_xml: str | None) -> dict[str, object] | None:
    """Report the coverage document's internal consistency, separately from any law.

    Deliberately NOT a ratcheted law. The defect is in ``coverage xml``'s rendering, not in this
    repository's code, so a ceiling here would be a ceiling on someone else's bug and tightening
    it would be outside this repository's control. It is surfaced because it is invisible to every
    summary: the header totals and the terminal report agree exactly while the body is missing 46%
    of the files, and a gate that reported only percentages would never see it.
    """
    from engine.certification_integrity import coverage_data

    candidate = coverage_xml or os.path.join(root, "coverage.xml")
    if not os.path.exists(candidate):
        return None
    try:
        report = coverage_data.parse(candidate, repository=root)
    except IntegrityError:
        return {"parseable": False}
    declared = report.declared_statements
    return {
        "parseable": True,
        "declared_statements": declared,
        "statements": report.statements,
        "files": len(report.files),
        "missing_from_body": report.missing_from_body,
        "missing_percent": (
            round(report.missing_from_body * 100.0 / declared, 2) if declared else 0.0
        ),
        "body_is_incomplete": report.body_is_incomplete,
        "ambiguous_file_keys": len(report.ambiguous_files),
    }
