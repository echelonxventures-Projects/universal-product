"""Verification Impact Engine — changed object to minimal required verification.

``./verify.sh`` costs ~74 minutes, of which pytest is 98%. The cost is structural: 59
coverage targets over 11 454 tests, evaluated against a whole-repository 90% floor. The
answer is not a weaker gate; it is knowing which verification a change actually
requires, and running the full gate when that is genuinely unknown.

This engine composes existing surfaces and builds no new graph:

============================  ====================================================
Substrate                     Owner
============================  ====================================================
file → file import edges      ``00-MASTER/UCOS-UGA-001/01-EXECUTABLE-OBJECT-REGISTRY``
                              (4 797 objects, 816 tests, 774 with resolved edges)
flattened relation edges      ``00-MASTER/UCOS-UGA-001/04-RELATIONSHIP-GRAPH``
ownership                     ``uga_engine.py::derive_owner``
evidence / certification      the registry's own per-object fields
diff base resolution          the fail-closed chain from ``ec1-ci.yml``
============================  ====================================================

**The engine fails wide.** Every path it cannot bound escalates to the whole suite, and
every escalation is named in the report. That asymmetry is deliberate: a verification
selector that errs narrow produces a green run which skipped the affected test, and no
amount of speed is worth that.

Authority: NONE — DERIVED TRUTH. It selects verification; it certifies nothing and
owns no gate.
"""

from __future__ import annotations

from engine.verification_impact.changes import changed_paths, working_tree_changes
from engine.verification_impact.graph import (
    ImpactError,
    ImpactGraph,
    ObjectRecord,
    load_graph,
)
from engine.verification_impact.impact import (
    ImpactReport,
    Scope,
    VerificationPlan,
    analyse,
    plan,
)

#: The published contract of this package.
IMPACT_CONTRACT: dict[str, object] = {
    "name": "Verification Impact Engine",
    "authority": "NONE — DERIVED TRUTH",
    "builds_new_graph": False,
    "fails_wide": True,
    "substrates": (
        "00-MASTER/UCOS-UGA-001/01-EXECUTABLE-OBJECT-REGISTRY.json",
        "00-MASTER/UCOS-UGA-001/04-RELATIONSHIP-GRAPH.json",
    ),
    "scopes": tuple(s.value for s in Scope),
}

__all__ = [
    "IMPACT_CONTRACT",
    "ImpactError",
    "ImpactGraph",
    "ImpactReport",
    "ObjectRecord",
    "Scope",
    "VerificationPlan",
    "analyse",
    "changed_paths",
    "load_graph",
    "plan",
    "working_tree_changes",
]
