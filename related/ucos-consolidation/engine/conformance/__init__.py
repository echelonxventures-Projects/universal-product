"""UAC-000001 — agnosticism conformance, measured rather than declared.

adr/0021 (UAP-001) states the Universal Agnostic Architecture Principle and then discloses, in
its own Consequences, that nothing enforces it: "no gate, invariant, or certification currently
checks conformance to this statement, and none is created by this document." This package is
that mechanism, built to the bar adr/0039 established — an abstraction with one implementation
is an assumption; an abstraction its own callers bypass is decoration.

It holds no authority. It names no technology. Every verdict is computed from the code as it
stands, and an axis is added by appending to the register (UCKP-ART-17).
"""

from engine.conformance.measure import (
    DECLARED_ABSENT,
    ENVELOPE_ONLY,
    PROVEN,
    REGISTER_PATH,
    SINGLE,
    AxisResult,
    ConformanceError,
    measure,
    measure_axis,
)

__all__ = [
    "AxisResult",
    "REGISTER_PATH",
    "ConformanceError",
    "measure",
    "measure_axis",
    "PROVEN",
    "SINGLE",
    "ENVELOPE_ONLY",
    "DECLARED_ABSENT",
]
