"""URI-000001 — the Test Generator.

Realizes canonical knowledge as *executable assertions*. This is the generator that makes
the rest of the system falsifiable: it emits a real pytest module whose every assertion is
derived from a canonical fact, so that if a generated artifact ever drifts from the
knowledge it claims to realize, a test fails.

Each emitted test corresponds to a claim URI makes:

* canonical source objects are present and still verify their content hash;
* every expected artifact for this target exists on disk;
* the architecture's layers are exactly the authority tiers canonical knowledge declares;
* the schema's enumerations are exactly the values canonical knowledge exhibits;
* the API's per-kind routes cover exactly the kinds present;
* the runtime declares every normative invariant and boots with all checks passing;
* the deployment gate ladder is ordered and fail-closed;
* every artifact records the knowledge seal it was generated from.

The generated module reads only artifacts and the canonical store, so it is runnable in
isolation from URI itself.
"""

from __future__ import annotations

from intelligence.realization.contracts import (
    FAMILY_ORDER,
    ArtifactFamily,
    GeneratedArtifact,
    MediaKind,
    identifier,
)
from intelligence.realization.generators.base import GenerationContext, Generator


class TestGenerator(Generator):
    """Derives the executable assertion suite for one realization target."""

    family = ArtifactFamily.TEST
    name = "uri.test"
    version = "1.0.0"

    def generate(self, context: GenerationContext) -> tuple[GeneratedArtifact, ...]:
        module = identifier(context.universe)
        return (
            self.text_artifact(
                context,
                relative_path=f"tests/test_{module}_realization.py",
                media=MediaKind.PYTHON,
                lines=self._module(context),
            ),
        )

    # -- derivation -----------------------------------------------------------

    def _expected_artifacts(self, context: GenerationContext) -> list[str]:
        """Every artifact the upstream families produced for this target."""
        paths: list[str] = []
        for family in FAMILY_ORDER:
            paths.extend(context.upstream_paths(family))
        return sorted(set(paths))

    def _module(self, context: GenerationContext) -> list[str]:
        target = context.target
        arch = context.upstream_artifact(ArtifactFamily.ARCHITECTURE, "-architecture.json")
        schema = context.upstream_artifact(ArtifactFamily.SCHEMA, ".schema.json")
        api = context.upstream_artifact(ArtifactFamily.API, "-openapi.json")
        runtime_desc = context.upstream_artifact(ArtifactFamily.RUNTIME, "-runtime.json")
        runtime_mod = context.upstream_artifact(ArtifactFamily.RUNTIME, "_runtime.py")
        deploy = context.upstream_artifact(ArtifactFamily.DEPLOYMENT, "-deployment.json")

        lines = self.provenance_comment(context, "#")
        lines += [
            f'"""Generated realization assertions for the {target.universe} universe.',
            "",
            "Every assertion below is derived from canonical knowledge. A failure means a",
            "generated artifact has drifted from the knowledge it claims to realize, or the",
            "canonical store itself was mutated after sealing.",
            "",
            "Run: python -m pytest realization/tests -q",
            '"""',
            "",
            "from __future__ import annotations",
            "",
            "import importlib.util",
            "import json",
            "from pathlib import Path",
            "from typing import Any",
            "",
            "import pytest",
            "",
            f'UNIVERSE = "{target.universe}"',
            f'TARGET_ID = "{target.target_id}"',
            f'KNOWLEDGE_SEAL = "{context.intake.knowledge_seal}"',
            f'TARGET_SEAL = "{target.seal}"',
            "SOURCE_CKOS = (",
        ]
        lines += [f'    "{cko_id}",' for cko_id in target.cko_ids]
        lines += [
            ")",
            "CANONICAL_KINDS = (" + "".join(f'"{k}", ' for k in target.kinds) + ")",
            "CANONICAL_LAYERS = (" + "".join(f'"{a}", ' for a in target.authorities) + ")",
            "INVARIANT_IDS = (" + "".join(f'"{inv.cko_id}", ' for inv in target.invariants) + ")",
            "EXPECTED_ARTIFACTS = (",
        ]
        lines += [f'    "{path}",' for path in self._expected_artifacts(context)]
        lines += [
            ")",
            f"ARCHITECTURE_ARTIFACT = {arch!r}",
            f"SCHEMA_ARTIFACT = {schema!r}",
            f"API_ARTIFACT = {api!r}",
            f"RUNTIME_DESCRIPTOR = {runtime_desc!r}",
            f"RUNTIME_MODULE = {runtime_mod!r}",
            f"DEPLOYMENT_ARTIFACT = {deploy!r}",
            "",
            "",
            "def _artifact_root() -> Path:",
            '    """Resolve the generated-artifact root by walking up to the repository."""',
            "    here = Path(__file__).resolve()",
            "    for candidate in here.parents:",
            '        if (candidate / "architecture").is_dir() and (candidate / "schema").is_dir():',
            "            return candidate",
            "    return here.parents[1]",
            "",
            "",
            "ROOT = _artifact_root()",
            "",
            "",
            "def _load_json(relative: str) -> dict[str, Any]:",
            "    path = ROOT / relative",
            "    if not path.is_file():",
            '        pytest.skip(f"artifact not materialized: {relative}")',
            '    return json.loads(path.read_text(encoding="utf-8"))',
            "",
            "",
            "def _canonical_base() -> Any:",
            "    from engine.knowledge.seed import build_seed_base",
            "    from engine.knowledge.store import KnowledgeStore",
            "",
            "    store = KnowledgeStore()",
            "    return store.load() if store.exists() else build_seed_base()",
            "",
            "",
            "# --- canonical source of truth -------------------------------------------",
            "",
            "",
            "def test_canonical_source_objects_are_present() -> None:",
            '    """Every object this realization derives from is still in the store."""',
            "    base = _canonical_base()",
            "    missing = [c for c in SOURCE_CKOS if not base.has_object(c)]",
            '    assert missing == [], f"canonical objects vanished: {missing}"',
            "",
            "",
            "def test_canonical_source_objects_verify_integrity() -> None:",
            '    """No source object was mutated after sealing (content-addressed check)."""',
            "    base = _canonical_base()",
            "    broken = [",
            "        c",
            "        for c in SOURCE_CKOS",
            "        if base.has_object(c) and not base.require_object(c).verify_integrity()",
            "    ]",
            '    assert broken == [], f"canonical integrity failure: {broken}"',
            "",
            "",
            "def test_canonical_objects_are_homed_in_this_universe() -> None:",
            '    """Universe homing is what made these objects one realization target."""',
            "    base = _canonical_base()",
            "    for cko_id in SOURCE_CKOS:",
            "        if base.has_object(cko_id):",
            "            assert base.require_object(cko_id).universe == UNIVERSE",
            "",
            "",
            "# --- artifact presence + provenance ---------------------------------------",
            "",
            "",
            '@pytest.mark.parametrize("relative", EXPECTED_ARTIFACTS)',
            "def test_expected_artifact_exists(relative: str) -> None:",
            '    """Every artifact planned for this target was materialized."""',
            '    assert (ROOT / relative).is_file(), f"missing artifact: {relative}"',
            "",
            "",
            '@pytest.mark.parametrize("relative", [',
            "    p for p in EXPECTED_ARTIFACTS if p.endswith('.json')",
            "])",
            "def test_json_artifact_records_knowledge_seal(relative: str) -> None:",
            '    """Provenance is not decorative: every artifact cites its knowledge seal."""',
            "    document = _load_json(relative)",
            '    assert document["knowledge_seal"] == KNOWLEDGE_SEAL',
            '    provenance = document["provenance"]',
            '    assert provenance["knowledge_seal"] == KNOWLEDGE_SEAL',
            '    assert provenance["target_id"] == TARGET_ID',
            '    assert provenance["source_ckos"] == list(SOURCE_CKOS)',
            "",
            "",
            "# --- architecture ---------------------------------------------------------",
            "",
            "",
            "def test_architecture_layers_match_canonical_authorities() -> None:",
            '    """Layers are the authority tiers canonical knowledge declares — no more."""',
            "    if ARCHITECTURE_ARTIFACT is None:",
            '        pytest.skip("no architecture artifact generated")',
            "    document = _load_json(ARCHITECTURE_ARTIFACT)",
            '    layers = [entry["layer"] for entry in document["layers"]]',
            "    assert layers == list(CANONICAL_LAYERS)",
            "",
            "",
            "def test_architecture_components_match_source_objects() -> None:",
            '    """One component per canonical object; nothing invented, nothing dropped."""',
            "    if ARCHITECTURE_ARTIFACT is None:",
            '        pytest.skip("no architecture artifact generated")',
            "    document = _load_json(ARCHITECTURE_ARTIFACT)",
            '    ids = sorted(entry["component_id"] for entry in document["components"])',
            "    assert ids == sorted(SOURCE_CKOS)",
            "",
            "",
            "def test_architecture_target_seal_is_stable() -> None:",
            '    """The descriptor cites the target seal it was derived from."""',
            "    if ARCHITECTURE_ARTIFACT is None:",
            '        pytest.skip("no architecture artifact generated")',
            '    assert _load_json(ARCHITECTURE_ARTIFACT)["target_seal"] == TARGET_SEAL',
            "",
            "",
            "# --- schema ---------------------------------------------------------------",
            "",
            "",
            "def test_schema_enumerations_match_canonical_values() -> None:",
            '    """The schema constrains `kind` to exactly the kinds present."""',
            "    if SCHEMA_ARTIFACT is None:",
            '        pytest.skip("no schema artifact generated")',
            "    document = _load_json(SCHEMA_ARTIFACT)",
            '    kind_property = document["properties"]["kind"]',
            '    enum = kind_property.get("enum")',
            "    if enum is None:",
            '        enum = kind_property["anyOf"][0]["enum"]',
            "    assert sorted(enum) == sorted(CANONICAL_KINDS)",
            "",
            "",
            "def test_schema_requires_canonical_identity() -> None:",
            '    """A record without identity or content hash is not a canonical record."""',
            "    if SCHEMA_ARTIFACT is None:",
            '        pytest.skip("no schema artifact generated")',
            "    document = _load_json(SCHEMA_ARTIFACT)",
            '    assert "cko_id" in document["required"]',
            '    assert "content_sha256" in document["required"]',
            '    assert document["additionalProperties"] is False',
            "",
            "",
            "# --- api ------------------------------------------------------------------",
            "",
            "",
            "def test_api_is_read_only() -> None:",
            '    """Realization holds no authority to author knowledge (UCKO-PRIN-0001)."""',
            "    if API_ARTIFACT is None:",
            '        pytest.skip("no api artifact generated")',
            "    document = _load_json(API_ARTIFACT)",
            "    methods = {",
            '        method for operations in document["paths"].values() for method in operations',
            "    }",
            '    assert methods == {"get"}, f"non-read method exposed: {sorted(methods)}"',
            "",
            "",
            "def test_api_kind_route_covers_every_canonical_kind() -> None:",
            '    """The per-kind route enumerates exactly the kinds present."""',
            "    if API_ARTIFACT is None:",
            '        pytest.skip("no api artifact generated")',
            "    document = _load_json(API_ARTIFACT)",
            "    enums: list[str] = []",
            '    for operations in document["paths"].values():',
            "        for operation in operations.values():",
            '            for parameter in operation.get("parameters", []):',
            '                if parameter["name"] == "kind":',
            '                    enums = parameter["schema"]["enum"]',
            "    assert sorted(enums) == sorted(CANONICAL_KINDS)",
            "",
            "",
            "# --- runtime --------------------------------------------------------------",
            "",
            "",
            "def test_runtime_declares_every_invariant() -> None:",
            '    """Every normative canonical statement is bound to runtime enforcement."""',
            "    if RUNTIME_DESCRIPTOR is None:",
            '        pytest.skip("no runtime descriptor generated")',
            "    document = _load_json(RUNTIME_DESCRIPTOR)",
            "    declared = sorted(",
            '        entry["cko_id"] for entry in document["invariant_enforcement"]',
            "    )",
            "    assert declared == sorted(INVARIANT_IDS)",
            "",
            "",
            "def test_runtime_checks_are_fail_closed() -> None:",
            '    """A check that cannot fail cannot enforce anything."""',
            "    if RUNTIME_DESCRIPTOR is None:",
            '        pytest.skip("no runtime descriptor generated")',
            "    document = _load_json(RUNTIME_DESCRIPTOR)",
            '    checks = document["mechanical_checks"]',
            "    assert checks",
            '    assert all(check["fail_closed"] is True for check in checks)',
            "",
            "",
            "def test_generated_runtime_boots_with_all_checks_passing() -> None:",
            '    """The generated runtime module is real, importable, and enforces its checks."""',
            "    if RUNTIME_MODULE is None:",
            '        pytest.skip("no runtime module generated")',
            "    path = ROOT / RUNTIME_MODULE",
            "    if not path.is_file():",
            '        pytest.skip(f"runtime module not materialized: {RUNTIME_MODULE}")',
            "    spec = importlib.util.spec_from_file_location(",
            '        f"uri_runtime_{UNIVERSE.lower()}", path',
            "    )",
            "    assert spec is not None and spec.loader is not None",
            "    module = importlib.util.module_from_spec(spec)",
            "    spec.loader.exec_module(module)",
            "    report = module.boot(_canonical_base())",
            '    assert report["ready"] is True, report["failed_checks"]',
            '    assert report["universe"] == UNIVERSE',
            "",
            "",
            "# --- deployment -----------------------------------------------------------",
            "",
            "",
            "def test_deployment_gate_ladder_is_ordered_and_fail_closed() -> None:",
            '    """Gates advance monotonically and none may be skipped."""',
            "    if DEPLOYMENT_ARTIFACT is None:",
            '        pytest.skip("no deployment artifact generated")',
            "    document = _load_json(DEPLOYMENT_ARTIFACT)",
            '    stages = document["stages"]',
            '    orders = [stage["order"] for stage in stages]',
            "    assert orders == sorted(orders)",
            "    assert orders == list(range(1, len(stages) + 1))",
            '    assert all(stage["fail_closed"] is True for stage in stages)',
            "",
            "",
            "def test_deployment_rollback_is_non_destructive() -> None:",
            '    """Rollback regenerates from canonical knowledge; it never destroys."""',
            "    if DEPLOYMENT_ARTIFACT is None:",
            '        pytest.skip("no deployment artifact generated")',
            "    document = _load_json(DEPLOYMENT_ARTIFACT)",
            '    assert document["rollback"]["destructive"] is False',
            '    assert document["rollback"]["reversible"] is True',
            '    for stage in document["stages"]:',
            '        assert stage["rollback"]["destructive"] is False',
            "",
        ]
        return lines


__all__ = ["TestGenerator"]
