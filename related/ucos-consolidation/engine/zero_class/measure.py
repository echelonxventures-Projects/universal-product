"""UZX-000001 — every zero-class stage, computed rather than declared.

WHAT THIS REFUSES TO DO. It never reads a stage. The register names classes, detectors and the
cases that prove a detector can fail; the stage is derived from what those actually do. A register
that could declare a class ratcheted would reproduce the defect the programme exists to catch,
which is the same reason engine/conformance never reads a disposition.
"""

from __future__ import annotations

import json
import os
import pathlib
import sys
import tempfile
from dataclasses import dataclass

REGISTER_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "zero-class-register.json")

DECLARED, DETECTED, ATTRIBUTED, RATCHETED, REMEDIATED = 1, 2, 3, 4, 5

#: A class whose detector cannot be resolved, run, or shown to fail in both directions. The
#: ceiling is zero because this register is new: every class admitted to it arrived with a working
#: detector, so any unenforced class is a regression rather than a backlog entry.
UNENFORCED_CEILING = 0


class ZeroClassError(RuntimeError):
    """The register is unusable. A fault, never a verdict."""


@dataclass(frozen=True, slots=True)
class ClassResult:
    class_id: str
    name: str
    stage: int
    measured: int | None
    ceiling: int | None
    catches: bool
    spares: bool
    reasons: tuple[str, ...]

    def to_dict(self) -> dict[str, object]:
        return {
            "class_id": self.class_id,
            "name": self.name,
            "stage": self.stage,
            "measured": self.measured,
            "ceiling": self.ceiling,
            "proves_it_catches": self.catches,
            "proves_it_spares": self.spares,
            "reasons": list(self.reasons),
        }


def _resolve(dotted: str) -> object:
    """Resolve against modules ALREADY IMPORTED, never importing one.

    Same inversion engine/conformance uses, for the same reason: Ω-4 holds
    unresolved_dynamic_sites MONOTONIC, and importing by a name computed from a register is an
    edge nothing can measure. The caller loads what the register names.
    """
    parts = dotted.split(".")
    for cut in range(len(parts), 0, -1):
        module = sys.modules.get(".".join(parts[:cut]))
        if module is None:
            continue
        target: object = module
        for attribute in parts[cut:]:
            try:
                target = getattr(target, attribute)
            except AttributeError as exc:
                raise ZeroClassError(f"{dotted}: no attribute {attribute}") from exc
        return target
    raise ZeroClassError(f"{dotted}: not loaded; the caller loads what the register names")


def _proves_both_directions(entry: dict) -> tuple[bool, bool, list[str]]:
    """Run the predicate against its own cases and report each direction separately.

    THE TWO DIRECTIONS ARE REPORTED APART because they fail differently. A detector that cannot
    catch is useless. A detector that cannot spare is WORSE: false positives make a floor
    unreachable, since the last entries resist every migration and the only way to close the count
    is to declare modules that never had a defect.
    """
    reasons: list[str] = []
    reference = entry.get("predicate")
    must_catch = entry.get("must_catch") or []
    must_spare = entry.get("must_not_catch") or []
    if not reference:
        if must_catch or must_spare:
            reasons.append("cases are declared but no predicate is named to run them against")
        return False, False, reasons

    # A dotted name when the register supplies it, a callable when a caller constructs an entry
    # in process. The register itself stays DATA — it can only name — but a test proving this
    # engine refuses a bad detector must be able to hand one over directly, and requiring it to
    # publish a module just to be refused would make the failing case harder to write than the
    # thing it guards.
    predicate = reference if callable(reference) else _resolve(str(reference))
    catches = spares = True
    with tempfile.TemporaryDirectory() as tmp:
        root = pathlib.Path(tmp)
        for index, source in enumerate(must_catch):
            probe = root / f"catch{index}.py"
            probe.write_text(str(source), encoding="utf-8")
            if not predicate(probe):
                catches = False
                reasons.append(f"must_catch[{index}] was not caught")
        for index, source in enumerate(must_spare):
            probe = root / f"spare{index}.py"
            probe.write_text(str(source), encoding="utf-8")
            if predicate(probe):
                spares = False
                reasons.append(f"must_not_catch[{index}] was caught: a false positive")
    return (catches and bool(must_catch)), (spares and bool(must_spare)), reasons


def stage_of(entry: dict) -> ClassResult:
    """The stage this class has actually reached, derived from what its detector does."""
    class_id, name = str(entry["class_id"]), str(entry["name"])
    reasons: list[str] = []
    stage = DECLARED if entry.get("definition") else 0
    if not stage:
        reasons.append("no definition; the class is named and not declared")

    detector_ref = entry.get("detector")
    measured: int | None = None
    if detector_ref:
        try:
            found = _resolve(str(detector_ref))()
            measured = len(found)
        except ZeroClassError as exc:
            reasons.append(f"detector unresolvable: {exc}")
        except Exception as exc:  # noqa: BLE001 - any failure keeps the class at DECLARED
            reasons.append(f"detector raised: {type(exc).__name__}: {exc}")
    else:
        reasons.append("no detector named")

    catches, spares, why = _proves_both_directions(entry)
    reasons.extend(why)
    if measured is not None and catches and spares:
        stage = DETECTED

    if stage >= DETECTED and measured is not None:
        stage = ATTRIBUTED  # the detector returns paths, which is the attribution

    ceiling = None
    if entry.get("ceiling"):
        try:
            ceiling = int(_resolve(str(entry["ceiling"])))  # type: ignore[arg-type]
        except (ZeroClassError, TypeError, ValueError) as exc:
            reasons.append(f"ceiling unresolvable: {exc}")
    if stage >= ATTRIBUTED and ceiling is not None and measured is not None and measured <= ceiling:
        stage = RATCHETED

    if stage >= RATCHETED and entry.get("remedy") in {"AUTOMATIC", "PROPOSED"}:
        stage = REMEDIATED

    return ClassResult(
        class_id=class_id,
        name=name,
        stage=stage,
        measured=measured,
        ceiling=ceiling,
        catches=catches,
        spares=spares,
        reasons=tuple(reasons),
    )


def load_register(path: str | None = None) -> dict:
    try:
        with open(path or REGISTER_PATH, encoding="utf-8") as handle:
            return json.load(handle)
    except FileNotFoundError:
        raise ZeroClassError(
            f"the zero-class register is absent: {path or REGISTER_PATH}"
        ) from None
    except ValueError as exc:
        raise ZeroClassError(f"the zero-class register is not valid JSON ({exc})") from None


def measure(path: str | None = None) -> tuple[ClassResult, ...]:
    """Every declared class, staged by measurement."""
    register = load_register(path)
    classes = register.get("classes")
    if not isinstance(classes, list) or not classes:
        raise ZeroClassError("the register declares no class")
    return tuple(stage_of(entry) for entry in classes if entry.get("detector") != _SELF)


def unenforced(path: str | None = None) -> tuple[str, ...]:
    """Class ids whose detector cannot be resolved, run, or shown to fail in both directions.

    ZX-SELF's own detector. The register measures itself by the rule it applies to everything
    else, because a register that exempted itself would repeat adr/0021 exactly, one level up.
    """
    return tuple(sorted(result.class_id for result in measure(path) if result.stage < DETECTED))


#: The self-referencing detector name, skipped when measuring so `unenforced` does not recurse.
_SELF = "engine.zero_class.measure.unenforced"


__all__ = [
    "ClassResult",
    "REGISTER_PATH",
    "UNENFORCED_CEILING",
    "ZeroClassError",
    "load_register",
    "measure",
    "stage_of",
    "unenforced",
]
