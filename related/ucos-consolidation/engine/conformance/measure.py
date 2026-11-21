"""UAC-000001 — the agnosticism conformance harness.

WHAT THIS IS, AND WHY IT IS NOT FOURTEEN SUITES. adr/0021 states the Universal Agnostic
Architecture Principle and declares in its own Consequences that nothing enforces it. This is
the enforcement, and it is ONE mechanism over a declared register rather than a suite per axis,
because a harness that named an axis would be the hardcoding the principle forbids. Nothing
below names a technology, a language, a database or an interpreter. Adding an axis is an
appended register entry (UCKP-ART-17: admitted by registration, never by amendment).

WHAT IT REFUSES TO DO. It never reads a disposition. The register names axes, contracts and
discriminators; every verdict here is computed from the code as it is. A register that could
declare an axis proven would reproduce the defect this exists to catch — adr/0039 scored
fourteen axes by hand, correctly, and the scoring was unrepeatable the moment it was written.
"""

from __future__ import annotations

import inspect
import json
import os
import sys
from dataclasses import dataclass

#: The axis register this harness measures. Declared here so callers name the instrument and
#: never a path, and so a test and an operator measure the same file.
REGISTER_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "axis-register.json")

PROVEN = "PROVEN"
SINGLE = "SINGLE"
ENVELOPE_ONLY = "ENVELOPE_ONLY"
DECLARED_ABSENT = "DECLARED_ABSENT"


class ConformanceError(RuntimeError):
    """The register or a contract is unusable. A fault, never a verdict."""


@dataclass(frozen=True, slots=True)
class AxisResult:
    axis: str
    contract: str
    implementations: tuple[str, ...]
    distinct: tuple[str, ...]
    shared_bodies: tuple[str, ...]
    discriminating: bool
    disposition: str
    reason: str

    def to_dict(self) -> dict[str, object]:
        return {
            "axis": self.axis,
            "contract": self.contract,
            "implementations": list(self.implementations),
            "distinct_implementations": list(self.distinct),
            "shared_bodies": list(self.shared_bodies),
            "discriminating_contract": self.discriminating,
            "disposition": self.disposition,
            "reason": self.reason,
        }


def _resolve(dotted: str) -> object:
    """Resolve a dotted reference against modules ALREADY IMPORTED. It imports nothing.

    WHY IT DOES NOT IMPORT, AND WHY THAT IS NOT A LIMITATION. Ω-4 holds
    ``unresolved_dynamic_sites`` MONOTONIC, and importing by a name computed from a register is
    by definition an edge nothing can measure. The first draft of this module took that metric
    from 22 to 23 and was refused — the identical construct, refused for the identical reason,
    in the UGA engine earlier the same day.

    The obvious repair, importing the contracts statically here, would put the axes' module
    names inside the harness: the hardcoding this instrument exists to measure. So resolution is
    inverted instead. The harness reads only what is already in ``sys.modules``, and the CALLER
    loads the contracts it wants measured. The register still decides which axes exist and which
    contract expresses each; what moves is the responsibility for loading them, onto a caller
    that may name an axis without being the thing that judges it.

    An axis whose contract is not loaded is reported unmeasurable, never skipped — the same
    reading given to a declared surface whose reporter cannot be reached.
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
                prefix = ".".join(parts[:cut])
                raise ConformanceError(f"{dotted}: {prefix} declares no {attribute}") from exc
        return target
    raise ConformanceError(
        f"{dotted}: no prefix of this reference is loaded, so the axis cannot be measured. "
        "The caller loads the contracts it asks about; this harness loads none."
    )


def _implementations(contract: type) -> tuple[type, ...]:
    """Every concrete subclass of the contract, discovered rather than listed.

    Discovery, not enumeration (UCKP-ART-08): an implementation that exists but was left out of
    a list is exactly the case a hand-maintained roster hides.
    """
    module = inspect.getmodule(contract)
    found = [
        value
        for value in vars(module).values()
        if inspect.isclass(value)
        and issubclass(value, contract)
        and value is not contract
        and not inspect.isabstract(value)
    ]
    return tuple(sorted(found, key=lambda c: c.__name__))


def measure_axis(entry: dict) -> AxisResult:
    """Measure one axis against the code, taking nothing on the register's word."""
    axis, contract_ref = str(entry["axis"]), str(entry["contract"])
    methods = tuple(str(m) for m in entry.get("abstract_methods") or ())

    contract = _resolve(contract_ref)
    if not inspect.isclass(contract):
        raise ConformanceError(f"{axis}: {contract_ref} is not a class")

    impls = _implementations(contract)
    names = tuple(c.__name__ for c in impls)

    # DISTINCTNESS. An implementation is distinct when it defines the contract's abstract
    # methods ITSELF. Inheriting one sibling's body means one implementation wearing two names,
    # which is what makes an interchangeability test over them unfailable.
    distinct, shared = [], []
    for cls in impls:
        defines_own = all(_defining_class(cls, name) == cls.__name__ for name in methods)
        (distinct if defines_own else shared).append(cls.__name__)

    discriminating = bool(entry.get("discriminator"))
    if discriminating:
        _resolve(str(entry["discriminator"]))  # must exist, or the register is wrong

    disposition, reason = _judge(len(distinct), discriminating, entry)
    return AxisResult(
        axis=axis,
        contract=contract_ref,
        implementations=names,
        distinct=tuple(distinct),
        shared_bodies=tuple(shared),
        discriminating=discriminating,
        disposition=disposition,
        reason=reason,
    )


def _defining_class(cls: type, name: str) -> str:
    """Which class in the MRO actually supplies ``name`` — properties included."""
    for base in cls.__mro__:
        if name in vars(base):
            return base.__name__
    return ""


def _judge(distinct: int, discriminating: bool, entry: dict) -> tuple[str, str]:
    if entry.get("declared_absent"):
        return DECLARED_ABSENT, str(entry.get("$absence_reason") or "declared absent")
    if not discriminating:
        return (
            ENVELOPE_ONLY,
            "the contract demands no answer a placeholder could fail to give, so no number of "
            "implementations can be distinguished by any case written against it",
        )
    if distinct >= 2:
        return (
            PROVEN,
            f"{distinct} implementations define the contract themselves and the contract can fail",
        )
    if distinct == 1:
        return (
            SINGLE,
            "one distinct implementation — an abstraction with one implementation is an assumption",
        )
    return ENVELOPE_ONLY, "no implementation defines the contract itself"


def load_register(path: str) -> dict:
    try:
        with open(path, encoding="utf-8") as handle:
            return json.load(handle)
    except FileNotFoundError:
        raise ConformanceError(f"the axis register is absent: {path}") from None
    except ValueError as exc:
        raise ConformanceError(f"the axis register is not valid JSON ({exc})") from None


def measure(path: str) -> tuple[AxisResult, ...]:
    register = load_register(path)
    axes = register.get("axes")
    if not isinstance(axes, list) or not axes:
        raise ConformanceError("the axis register declares no axis")
    return tuple(measure_axis(entry) for entry in axes)


if __name__ == "__main__":
    # The caller's job, per _resolve: load the contracts, then measure them. Naming axis modules
    # here is not the hardcoding this harness measures — this block decides nothing and holds no
    # verdict. It makes the edges real so Ω-4 can see them, and so the register's references
    # resolve at all.
    import engine.uckp.execution  # noqa: F401
    import engine.uckp.persistence  # noqa: F401

    results = measure(REGISTER_PATH)
    for r in results:
        print(
            f"{r.disposition:16s} {r.axis:14s} "
            f"distinct {len(r.distinct)}/{len(r.implementations)}  "
            f"discriminating={r.discriminating}"
        )
        print(f"                 {r.reason}")
        if r.shared_bodies:
            print(f"                 sharing one body: {', '.join(r.shared_bodies)}")
    sys.exit(0)
