"""Curated knowledge overlay — DECLARATIVE, not derived.

This module holds the small amount of curated engineering knowledge that cannot
be mechanically derived from evidence: how capability *categories* map to reuse
dispositions, which layers are replacement-prohibited, the known AEOS execution-
spine gap list (from ADR-0002), and the dimension→completeness scoring map used
by the progress index.

It is deliberately isolated and labelled so the boundary between DERIVED facts
(everything else in the engine) and CURATED knowledge (here) is explicit. The
engine VERIFIES this overlay against evidence (e.g. it confirms each declared
location exists) rather than trusting it blindly. This mirrors the repository's
own pattern (``00-BOOK/tools/config.py`` declares classification rules; ``ukb.py``
derives the values).
"""

from __future__ import annotations

# Category → (reuse disposition, replacement_prohibited, authority, status). Derived
# facts such as coverage/tests are NOT here; only the durable engineering policy is.
# Every posture below is quoted from the code root's own package docstring, which is
# the repository's own statement about that layer.
CATEGORY_POLICY: dict[str, dict[str, object]] = {
    "engine": {
        "reuse": "REUSE_AS_IS/COMPOSE",
        "replacement_prohibited": True,
        "authority": "EC-1 CERTIFIED",
        "status": "CERTIFIED",
    },
    "platform": {
        "reuse": "REUSE/COMPOSE",
        "replacement_prohibited": True,
        "authority": "EC-2 CLOSED/FROZEN",
        "status": "IMPLEMENTED",
    },
    "data": {
        "reuse": "REUSE/EXTEND",
        "replacement_prohibited": False,
        "authority": "EC-3 BAND 10 (DATA) REALIZATION",
        "status": "IMPLEMENTED",
    },
    "service": {
        "reuse": "REUSE/EXTEND",
        "replacement_prohibited": False,
        "authority": "EC-3 BAND 11 (SERVICE) REALIZATION",
        "status": "IMPLEMENTED",
    },
    "application": {
        "reuse": "REUSE/EXTEND",
        "replacement_prohibited": False,
        "authority": "EC-3 BAND 12 (APPLICATION) REALIZATION",
        "status": "IMPLEMENTED",
    },
    "infrastructure": {
        "reuse": "REUSE/EXTEND",
        "replacement_prohibited": False,
        "authority": "EC-3 BAND 13 (INFRASTRUCTURE) REALIZATION",
        "status": "IMPLEMENTED",
    },
    "intelligence": {
        "reuse": "REUSE/EXTEND",
        "replacement_prohibited": False,
        "authority": "ADDITIVE (AUTHORITY=NONE)",
        "status": "IMPLEMENTED",
    },
    "automation": {
        "reuse": "REUSE/EXTEND",
        "replacement_prohibited": False,
        "authority": "ACTIVE",
        "status": "IMPLEMENTED",
    },
    "operational_memory": {
        "reuse": "REUSE/EXTEND",
        "replacement_prohibited": False,
        "authority": "ACTIVE (AUTHORITY=NONE)",
        "status": "IMPLEMENTED",
    },
    "orchestration_spec": {
        "reuse": "REALIZE_BY_COMPOSITION",
        "replacement_prohibited": False,
        "authority": "SPEC (AUTHORITY=NONE)",
        "status": "PLANNED",
    },
    "corpus": {
        "reuse": "REUSE_AS_IS (read-only)",
        "replacement_prohibited": True,
        "authority": "FROZEN / GOVERNANCE",
        "status": "IMPLEMENTED",
    },
}

# Fallback for a category with no declared policy. Fail-closed: an undeclared
# category is reported as INDETERMINATE rather than inheriting another layer's
# authority. Inheriting ``engine``'s policy would have any newly discovered code
# root falsely claim EC-1 certification — a fabricated fact.
UNCLASSIFIED_POLICY: dict[str, object] = {
    "reuse": "INDETERMINATE",
    "replacement_prohibited": False,
    "authority": "UNCLASSIFIED (no category policy declared)",
    "status": "INDETERMINATE",
}


def policy_for(category: str) -> dict[str, object]:
    """Return the declared policy for *category*, or the fail-closed fallback."""
    return CATEGORY_POLICY.get(category, UNCLASSIFIED_POLICY)


# Known AEOS execution-spine gaps (curated from ADR-0002 determination). The
# engine reports these as PLANNED work; it does NOT implement them.
KNOWN_SPINE_GAPS: list[dict[str, str]] = [
    {"id": "G-01", "missing": "Executable CCE (completeness runtime)", "severity": "HIGH"},
    {
        "id": "G-02",
        "missing": "Executable CIOA (state/critical-path/next/forecast runtime)",
        "severity": "HIGH",
    },
    {"id": "G-03", "missing": "Execution scheduler", "severity": "HIGH"},
    {"id": "G-04", "missing": "Lease manager (concurrency)", "severity": "MEDIUM"},
    {"id": "G-05", "missing": "Execution transaction manager", "severity": "MEDIUM"},
    {"id": "G-06", "missing": "Recovery + resume managers", "severity": "MEDIUM"},
    {"id": "G-07", "missing": "Git orchestrator", "severity": "MEDIUM"},
    {"id": "G-08", "missing": "Unified event-ledger reader", "severity": "MEDIUM"},
    {"id": "G-09", "missing": "AI adapter layer (multi-executor)", "severity": "HIGH"},
    {"id": "G-10", "missing": "Human adapter", "severity": "LOW"},
    {"id": "G-11", "missing": "Mission control runtime", "severity": "MEDIUM"},
    {"id": "G-12", "missing": "Universal AEOS CLI", "severity": "MEDIUM"},
]

# Dimension status → completeness score in [0,1] for the progress index.
# BLOCKED scores 0 in the literal index; the engine ALSO computes a reconciled
# index that credits stale-but-locally-passing dimensions (see analysis.py).
DIMENSION_SCORE: dict[str, float] = {
    "APPROVED": 1.0,
    "CERTIFIED": 1.0,
    "IMPLEMENTED": 1.0,
    "COMPLETE": 1.0,
    "FINAL": 1.0,
    "IN_PROGRESS": 0.5,
    "PARTIALLY_IMPLEMENTED": 0.5,
    "BLOCKED": 0.0,
    "NOT_STARTED": 0.0,
    "NOT_PLANNED": 0.0,
    "INDETERMINATE": 0.0,
}

# Dimensions whose BLOCKED status is contradicted by local unit evidence
# (100% coverage) and therefore credited in the reconciled progress index.
LOCALLY_VERIFIABLE_DIMENSIONS = ("build", "unit_testing")
