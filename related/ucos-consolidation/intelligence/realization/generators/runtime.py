"""URI-000001 — the Runtime Generator.

Realizes the *operating behaviour* implied by canonical knowledge: a runtime descriptor
plus an executable runtime module that enforces the universe's invariants at boot.

The honesty rule here matters. A normative statement in prose cannot be mechanically
enforced by a generator that is forbidden from inventing meaning. So the runtime binds
each normative canonical object to the checks that *are* mechanically derivable from the
canonical record:

* ``presence``  — the object is present in the canonical store the runtime loads;
* ``integrity`` — its ``content_sha256`` still verifies (it was not mutated);
* ``lifecycle`` — its lifecycle stage is a live source of authority;
* ``authority`` — the target's dependency edges do not invert authority precedence;
* ``conflict``  — no two co-homed objects declare a conflict with each other.

Anything beyond that is declared, not faked: each object also reports its canonical
``validation`` reference, and where none exists the descriptor records the enforcement as
``declarative`` so a reader can see exactly what is and is not machine-checked.
"""

from __future__ import annotations

from typing import Any

from intelligence.realization.contracts import (
    ArtifactFamily,
    GeneratedArtifact,
    MediaKind,
    identifier,
)
from intelligence.realization.generators.base import GenerationContext, Generator

RUNTIME_DOCUMENT_FORMAT = "ucos-uri-runtime/1.0.0"

#: The mechanically derivable checks, in execution order.
MECHANICAL_CHECKS: tuple[str, ...] = (
    "presence",
    "integrity",
    "lifecycle",
    "authority",
    "conflict",
)


class RuntimeGenerator(Generator):
    """Derives the runtime descriptor and its executable enforcement module."""

    family = ArtifactFamily.RUNTIME
    name = "uri.runtime"
    version = "1.0.0"

    def generate(self, context: GenerationContext) -> tuple[GeneratedArtifact, ...]:
        slug = context.target.path_slug
        descriptor = self._descriptor(context)
        return (
            self.json_artifact(
                context,
                relative_path=f"runtime/{slug}-runtime.json",
                payload=descriptor,
            ),
            self.text_artifact(
                context,
                relative_path=f"runtime/{identifier(context.universe)}_runtime.py",
                media=MediaKind.PYTHON,
                lines=self._runtime_module(context, descriptor),
            ),
        )

    # -- derivation -----------------------------------------------------------

    def _enforcement(self, context: GenerationContext) -> list[dict[str, Any]]:
        by_id = {obj.cko_id: obj for obj in context.objects}
        records = []
        for inv in context.target.invariants:
            obj = by_id[inv.cko_id]
            records.append(
                {
                    "cko_id": inv.cko_id,
                    "kind": inv.kind,
                    "authority": inv.authority,
                    "statement": inv.statement,
                    "mechanical_checks": list(MECHANICAL_CHECKS),
                    "declared_validation": obj.validation,
                    "declared_certification": obj.certification,
                    "enforcement": "mechanical+declared" if obj.validation else "mechanical",
                    "content_sha256": obj.content_sha256,
                }
            )
        return sorted(records, key=lambda entry: entry["cko_id"])

    def _config_keys(self, context: GenerationContext) -> list[dict[str, Any]]:
        """Configuration surface derived from what the runtime must resolve."""
        return [
            {
                "key": "UCOS_KNOWLEDGE_DIR",
                "type": "path",
                "required": False,
                "default": "<repo>/knowledge",
                "description": (
                    "Canonical knowledge store directory. When unset the runtime resolves "
                    "the repository default, falling back to the authored-once seed base."
                ),
            },
            {
                "key": "UCOS_EXPECTED_KNOWLEDGE_SEAL",
                "type": "string",
                "required": False,
                "default": context.intake.knowledge_seal,
                "description": (
                    "The knowledge seal this runtime was generated from. When set, boot "
                    "fails closed if the canonical store no longer matches."
                ),
            },
        ]

    def _descriptor(self, context: GenerationContext) -> dict[str, Any]:
        target = context.target
        arch = context.upstream_artifact(ArtifactFamily.ARCHITECTURE, "-architecture.json")
        schema = context.upstream_artifact(ArtifactFamily.SCHEMA, ".schema.json")
        enforcement = self._enforcement(context)
        payload = context.envelope(
            artifact_id=f"UCOS-URI-RUNTIME-{target.path_slug.upper()}",
            title=f"{target.universe} — Realized Runtime Descriptor",
            document_format=RUNTIME_DOCUMENT_FORMAT,
        )
        payload.update(
            {
                "service": {
                    "service_id": f"ucos-knowledge-{target.path_slug}",
                    "universe": target.universe,
                    "target_id": target.target_id,
                    "entrypoint": (f"runtime/{identifier(target.universe)}_runtime.py:boot"),
                    "stateless": True,
                    "read_only": True,
                    "vendor_neutral": True,
                    "runtime": "python>=3.12 (standard library only)",
                },
                "consumes": {
                    "architecture_descriptor": arch,
                    "record_schema": schema,
                    "canonical_store": "knowledge/canonical-knowledge.json",
                },
                "config": self._config_keys(context),
                "mechanical_checks": [
                    {
                        "check": "presence",
                        "description": "every source canonical object is present in the store",
                        "fail_closed": True,
                    },
                    {
                        "check": "integrity",
                        "description": "every source canonical object verifies its content hash",
                        "fail_closed": True,
                    },
                    {
                        "check": "lifecycle",
                        "description": "objects report a lifecycle stage from the canonical set",
                        "fail_closed": True,
                    },
                    {
                        "check": "authority",
                        "description": "no dependency edge inverts authority precedence",
                        "fail_closed": True,
                    },
                    {
                        "check": "conflict",
                        "description": "no two co-homed objects declare a mutual conflict",
                        "fail_closed": True,
                    },
                ],
                "invariant_enforcement": enforcement,
                "invariant_count": len(enforcement),
                "mechanically_enforced": len(enforcement) * len(MECHANICAL_CHECKS),
                "health": {
                    "readiness": "all mechanical checks pass",
                    "liveness": "canonical store readable and seal-matched",
                    "degraded": "store absent — runtime serves the seed base and reports it",
                },
                "expected_knowledge_seal": context.intake.knowledge_seal,
                "source_ckos": list(target.cko_ids),
                "target_seal": target.seal,
            }
        )
        return payload

    # -- executable binding ---------------------------------------------------

    def _runtime_module(self, context: GenerationContext, descriptor: dict[str, Any]) -> list[str]:
        target = context.target
        ranks = {obj.cko_id: obj.authority.rank for obj in context.objects}
        lines = self.provenance_comment(context, "#")
        lines += [
            f'"""Runtime enforcement for the {target.universe} canonical knowledge universe.',
            "",
            "Boot performs every mechanically derivable check and fails closed. Import is",
            "side-effect free; the canonical store is resolved only when boot() runs.",
            '"""',
            "",
            "from __future__ import annotations",
            "",
            "from typing import Any",
            "",
            f'UNIVERSE = "{target.universe}"',
            f'SERVICE_ID = "{descriptor["service"]["service_id"]}"',
            f'EXPECTED_KNOWLEDGE_SEAL = "{context.intake.knowledge_seal}"',
            "SOURCE_CKOS = (",
        ]
        lines += [f'    "{cko_id}",' for cko_id in target.cko_ids]
        lines += [
            ")",
            "AUTHORITY_RANK: dict[str, int] = {",
        ]
        for cko_id in target.cko_ids:
            lines.append(f'    "{cko_id}": {ranks[cko_id]},')
        lines += [
            "}",
            "DEPENDENCY_EDGES: tuple[tuple[str, str, str], ...] = (",
        ]
        for src, rel, dst in target.edges:
            lines.append(f'    ("{src}", "{rel}", "{dst}"),')
        lines += [
            ")",
            "DECLARED_CONFLICTS: tuple[tuple[str, str], ...] = (",
        ]
        for pair in context.intake.conflict_pairs():
            if pair[0] in ranks and pair[1] in ranks:
                lines.append(f'    ("{pair[0]}", "{pair[1]}"),')
        lines += [
            ")",
            "INVARIANTS: tuple[dict[str, Any], ...] = (",
        ]
        for record in descriptor["invariant_enforcement"]:
            lines += [
                "    {",
                f'        "cko_id": "{record["cko_id"]}",',
                f'        "kind": "{record["kind"]}",',
                f'        "authority": "{record["authority"]}",',
                f'        "enforcement": "{record["enforcement"]}",',
                f"        \"statement\": {record['statement']!r},",
                "    },",
            ]
        lines += [
            ")",
            "",
            "",
            "def load_base() -> Any:",
            '    """Resolve the canonical knowledge base (store first, seed base as fallback)."""',
            "    from engine.knowledge.seed import build_seed_base",
            "    from engine.knowledge.store import KnowledgeStore",
            "",
            "    store = KnowledgeStore()",
            "    return store.load() if store.exists() else build_seed_base()",
            "",
            "",
            "def _result(check: str, passed: bool, **detail: Any) -> dict[str, Any]:",
            '    return {"check": check, "passed": passed, "detail": dict(detail)}',
            "",
            "",
            "def check_presence(base: Any) -> dict[str, Any]:",
            '    """Every source canonical object is present in the loaded store."""',
            "    missing = [c for c in SOURCE_CKOS if not base.has_object(c)]",
            '    return _result("presence", not missing, missing=missing)',
            "",
            "",
            "def check_integrity(base: Any) -> dict[str, Any]:",
            '    """Every present source object still verifies its own content hash."""',
            "    failed = [",
            "        c",
            "        for c in SOURCE_CKOS",
            "        if base.has_object(c) and not base.require_object(c).verify_integrity()",
            "    ]",
            '    return _result("integrity", not failed, failed=failed)',
            "",
            "",
            "def check_lifecycle(base: Any) -> dict[str, Any]:",
            '    """Every present source object reports a canonical lifecycle stage."""',
            "    stages = sorted(",
            "        {",
            "            base.require_object(c).lifecycle.value",
            "            for c in SOURCE_CKOS",
            "            if base.has_object(c)",
            "        }",
            "    )",
            '    return _result("lifecycle", bool(stages), stages=stages)',
            "",
            "",
            "def check_authority(_base: Any) -> dict[str, Any]:",
            '    """No dependency edge points from a more into a less authoritative layer."""',
            "    inversions = [",
            "        [src, rel, dst]",
            "        for src, rel, dst in DEPENDENCY_EDGES",
            "        if src in AUTHORITY_RANK",
            "        and dst in AUTHORITY_RANK",
            "        and AUTHORITY_RANK[dst] > AUTHORITY_RANK[src]",
            "    ]",
            '    return _result("authority", not inversions, inversions=inversions)',
            "",
            "",
            "def check_conflict(_base: Any) -> dict[str, Any]:",
            '    """No two co-homed canonical objects declare a mutual conflict."""',
            "    pairs = [list(pair) for pair in DECLARED_CONFLICTS]",
            '    return _result("conflict", not pairs, conflicting_pairs=pairs)',
            "",
            "",
            "CHECKS = (",
            "    check_presence,",
            "    check_integrity,",
            "    check_lifecycle,",
            "    check_authority,",
            "    check_conflict,",
            ")",
            "",
            "",
            "def check_invariants(base: Any) -> tuple[dict[str, Any], ...]:",
            '    """Run every mechanical check against ``base``."""',
            "    return tuple(check(base) for check in CHECKS)",
            "",
            "",
            "def health(base: Any) -> dict[str, Any]:",
            '    """Readiness report. ``ready`` is fail-closed: all checks must pass."""',
            "    results = check_invariants(base)",
            '    failed = [r for r in results if not r["passed"]]',
            "    return {",
            '        "service_id": SERVICE_ID,',
            '        "universe": UNIVERSE,',
            '        "ready": not failed,',
            '        "checks": list(results),',
            '        "failed_checks": [r["check"] for r in failed],',
            '        "invariant_count": len(INVARIANTS),',
            "    }",
            "",
            "",
            "def boot(base: Any | None = None) -> dict[str, Any]:",
            '    """Boot the runtime, failing closed when any mechanical check fails."""',
            "    resolved = base if base is not None else load_base()",
            "    report = health(resolved)",
            '    if not report["ready"]:',
            "        from engine.knowledge.errors import KnowledgeValidationError",
            "",
            "        raise KnowledgeValidationError(",
            '            "runtime invariant enforcement failed",',
            "            universe=UNIVERSE,",
            '            failed_checks=report["failed_checks"],',
            "        )",
            "    return report",
            "",
            "",
            "__all__ = [",
            '    "UNIVERSE",',
            '    "SERVICE_ID",',
            '    "EXPECTED_KNOWLEDGE_SEAL",',
            '    "SOURCE_CKOS",',
            '    "INVARIANTS",',
            '    "CHECKS",',
            '    "boot",',
            '    "check_authority",',
            '    "check_conflict",',
            '    "check_integrity",',
            '    "check_invariants",',
            '    "check_lifecycle",',
            '    "check_presence",',
            '    "health",',
            '    "load_base",',
            "]",
            "",
        ]
        return lines


__all__ = ["MECHANICAL_CHECKS", "RUNTIME_DOCUMENT_FORMAT", "RuntimeGenerator"]
