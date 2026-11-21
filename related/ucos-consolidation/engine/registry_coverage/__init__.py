"""RCM — the Registry Coverage Matrix.

Coverage intelligence over registration, derived on every call and stored nowhere.

It answers *what governed objects exist, where are they registered, who owns the
registration plane, and what coverage gaps exist* — and it answers by reading the
instruments that already hold those answers. It registers nothing, owns nothing and mints
nothing; deleting it changes no registration and no verdict.

The constraint that shapes every design choice here: **the matrix must never become the
141st registry.** It keeps no object record of its own, because a stored copy would be the
duplicate catalogue it exists to detect.
"""

from __future__ import annotations

from engine.registry_coverage.matrix import (
    COVERED,
    DUPLICATE_REGISTRATION,
    PARTIALLY_COVERED,
    UNREGISTERED,
    AuthorityGap,
    CoverageError,
    Declarations,
    Plane,
    build,
    digest,
    load_declarations,
    rendered,
    validate,
    verify,
)

__all__ = [
    "COVERED",
    "DUPLICATE_REGISTRATION",
    "PARTIALLY_COVERED",
    "UNREGISTERED",
    "AuthorityGap",
    "CoverageError",
    "Declarations",
    "Plane",
    "build",
    "digest",
    "load_declarations",
    "rendered",
    "validate",
    "verify",
]
