"""Universal Verification Intelligence (UVI-000001) — which verification a change requires.

``./verify.sh`` executed one plan for every caller. Measured on the certification
baseline: 11 628 tests, 97.61%% coverage, every gate green, 2 814 s in pytest and
coverage alone — and a developer changing one module paid all of it.

The response that destroys assurance is to delete gates. This engine does the other
thing: it composes surfaces the repository already publishes into an answer to "which
verification does this change actually require, and in what order may it be executed",
and leaves every obligation exactly where it was.

============================  ==========================================================
Component                     Module
============================  ==========================================================
Verification Mode Constitution ``constitution`` — modes as DATA, in the declaration
Verification Stage Registry    ``constitution`` — every declared stage, classified
Test Object Registry           ``registry`` — collectible test objects, priced
Change Impact Analysis         ``engine.verification_impact`` — reused, not re-derived
Dependency Driven Selection    ``selection`` — five substrates, layered
Evidence Reuse                 ``evidence`` — content-addressed, never for certification
Parallel Execution             ``execution`` — deterministic shards, one combined floor
Deterministic Verification     ``plan`` — no clock, no host, byte-identical twice
============================  ==========================================================

Authority: NONE — DERIVED TRUTH. It selects and schedules verification; it certifies
nothing, owns no gate, and holds no counter.
"""

from __future__ import annotations

from engine.verification_intelligence.constitution import (
    Constitution,
    load_constitution,
    load_declaration,
)
from engine.verification_intelligence.execution import plan_shards, run_tests
from engine.verification_intelligence.model import (
    Action,
    Coverage,
    Mode,
    Plan,
    Selection,
    SelectionResult,
    Shard,
    StagePlan,
    StageSpec,
    TestObject,
    VerificationIntelligenceError,
)
from engine.verification_intelligence.plan import build_plan, plan_digest, plan_json, plan_tsv
from engine.verification_intelligence.registry import build_test_registry, load_substrates
from engine.verification_intelligence.selection import select

#: The published contract of this package.
VERIFICATION_INTELLIGENCE_CONTRACT: dict[str, object] = {
    "name": "Universal Verification Intelligence",
    "artifact_id": "UVI-000001",
    "authority": "NONE — DERIVED TRUTH",
    "builds_new_graph": False,
    "fails_wide": True,
    "certifies": False,
}

__all__ = [
    "VERIFICATION_INTELLIGENCE_CONTRACT",
    "Action",
    "Constitution",
    "Coverage",
    "Mode",
    "Plan",
    "Selection",
    "SelectionResult",
    "Shard",
    "StagePlan",
    "StageSpec",
    "TestObject",
    "VerificationIntelligenceError",
    "build_plan",
    "build_test_registry",
    "load_constitution",
    "load_declaration",
    "load_substrates",
    "plan_digest",
    "plan_json",
    "plan_shards",
    "plan_tsv",
    "run_tests",
    "select",
]
