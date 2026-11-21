"""UCI-000001 — Universal Certification Integrity.

The subject of this package is not coverage. It is the QUESTION coverage answers, and whether
that question is the one the repository believes it is asking.

WHAT PRODUCED IT, stated as measurement rather than intent.

``coverage.xml`` reported 97.9% of 83,142 statements. The tracked non-test Python surface is
182,202 statements. So the figure was true and answered a question about 50.5% of the executable
surface, and nothing anywhere recorded that the other 90,230 statements were outside it. That is
not a low percentage; it is a percentage whose denominator was never a governed object.
UCOS-COV-SCOPE-001 had already closed one instance of this for ``engine/`` and ``platform/``
packages. It could not close the general case, because its enumeration was keyed on
``__init__.py`` and its trees were only two.

The unmeasured surface, measured:

    00-BOOK/tools, scripts/, root utilities   493 files   57,086 statements
    00-MASTER/*/*_engine.py                    39 files   20,359 statements  <- UEC gate engines
    intelligence/                              65 files    5,565 statements  <- in testpaths only
    engine/recursive_knowledge                 16 files    2,849 statements  <- namespace package
    00-MASTER/ other executables               10 files    2,237 statements

The 39 ``00-MASTER`` engines are the sharpest case. Every one of them is an enforcement artifact
that UEC-000001 governs by name, several are ``verify.sh`` certification stages, and their
covered fraction was measured by nothing at all. A gate whose own executed fraction is unknown
is a gate that can rot into a no-op and keep reporting OPEN.

WHAT THIS PACKAGE ADDS, AND WHAT IT DELIBERATELY DOES NOT.

It adds five measurements the repository could not previously make:

  * ``surface``          — every executable object, and whether the denominator contains it
  * ``immutable``        — verification from a frozen ``git archive`` extraction of a named SHA
  * ``reproducibility``  — the same measurement N times, compared line-set by line-set
  * ``shards``           — that combining shards equals one whole run, per line not per percent
  * ``order``            — that the verdict does not depend on the order tests ran in

It does NOT change any threshold, does not widen any exemption, and does not compute a number
that replaces an existing one. Where its measurement is stricter than an existing measurement
— ``surface`` counts invocation PLANE TYPES where UEC-L-06 counts distinct invoking texts, so
thirty-three workflows are one CI plane here and thirty-three planes there — both figures are
reported side by side and the existing ratchet is left alone. A stricter measurement that
silently overwrote a governed ceiling would be an ungoverned adoption event.

AUTHORITY = NONE (DERIVED TRUTH). Nothing here legislates. Every function reads tracked
repository content and reports what it says. The package writes no register: like
``engine/enforcement_closure``, its observations go to stdout and its expectations live in data,
because an observation that can rewrite its own expectation is not a measurement.
"""

from __future__ import annotations

__all__ = ["model", "surface", "coverage_data"]
