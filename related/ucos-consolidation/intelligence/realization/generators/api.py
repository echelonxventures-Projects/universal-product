"""URI-000001 — the API Generator.

Realizes the *read surface* of canonical knowledge. The resource set is derived, not
designed: one collection per universe, one item route keyed by canonical id, one
sub-collection per knowledge kind actually present, plus the normative projections
(invariants, layers). Response schemas ``$ref`` the artifact the Schema Generator
produced for the same target, so the contract and the validator are the same fact.

Two projections:

* an OpenAPI 3.1 description — the contract;
* a framework-neutral Python route table — the executable binding. It imports nothing at
  module scope beyond the standard library, resolves the canonical store lazily, and is
  read-only by construction (there is no write route, because URI has no authority to
  author knowledge).
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

OPENAPI_VERSION = "3.1.0"
API_DOCUMENT_FORMAT = "ucos-uri-api/1.0.0"


class ApiGenerator(Generator):
    """Derives the read-only API surface for one realization target."""

    family = ArtifactFamily.API
    name = "uri.api"
    version = "1.0.0"

    def generate(self, context: GenerationContext) -> tuple[GeneratedArtifact, ...]:
        slug = context.target.path_slug
        return (
            self.json_artifact(
                context,
                relative_path=f"api/{slug}-openapi.json",
                payload=self._openapi(context),
            ),
            self.text_artifact(
                context,
                relative_path=f"api/{identifier(context.universe)}_routes.py",
                media=MediaKind.PYTHON,
                lines=self._routes_module(context),
            ),
        )

    # -- derivation -----------------------------------------------------------

    def _base_path(self, context: GenerationContext) -> str:
        return f"/knowledge/{context.target.path_slug}"

    def _operations(self, context: GenerationContext) -> list[dict[str, Any]]:
        """The derived operation set: collection, item, per-kind, and normative views."""
        base = self._base_path(context)
        operations: list[dict[str, Any]] = [
            {
                "operation_id": "list_objects",
                "method": "get",
                "path": f"{base}/objects",
                "summary": f"List every canonical object homed in {context.universe}",
                "collection": True,
                "parameters": [],
            },
            {
                "operation_id": "get_object",
                "method": "get",
                "path": f"{base}/objects/{{cko_id}}",
                "summary": "Fetch one canonical object by its canonical id",
                "collection": False,
                "parameters": [
                    {
                        "name": "cko_id",
                        "in": "path",
                        "required": True,
                        "schema": {"type": "string", "enum": list(context.target.cko_ids)},
                        "description": "Canonical object identifier.",
                    }
                ],
            },
            {
                "operation_id": "list_kinds",
                "method": "get",
                "path": f"{base}/kinds",
                "summary": "List the knowledge kinds present in this universe",
                "collection": False,
                "parameters": [],
                "response_schema": {
                    "type": "array",
                    "items": {"type": "string", "enum": list(context.target.kinds)},
                },
            },
            {
                "operation_id": "list_objects_by_kind",
                "method": "get",
                "path": f"{base}/kinds/{{kind}}/objects",
                "summary": "List canonical objects of one knowledge kind",
                "collection": True,
                "parameters": [
                    {
                        "name": "kind",
                        "in": "path",
                        "required": True,
                        "schema": {"type": "string", "enum": list(context.target.kinds)},
                        "description": "Knowledge kind present in this universe.",
                    }
                ],
            },
            {
                "operation_id": "list_invariants",
                "method": "get",
                "path": f"{base}/invariants",
                "summary": "List the normative invariants this universe imposes",
                "collection": False,
                "parameters": [],
                "response_schema": {"$ref": "#/components/schemas/Invariant"},
                "response_is_array": True,
            },
            {
                "operation_id": "list_layers",
                "method": "get",
                "path": f"{base}/layers",
                "summary": "List the authority layers present in this universe",
                "collection": False,
                "parameters": [],
                "response_schema": {
                    "type": "array",
                    "items": {
                        "type": "string",
                        "enum": list(context.target.authorities),
                    },
                },
            },
        ]
        return operations

    def _openapi(self, context: GenerationContext) -> dict[str, Any]:
        target = context.target
        schema_ref = context.upstream_artifact(ArtifactFamily.SCHEMA, ".schema.json")
        record_schema: dict[str, Any] = (
            {"$ref": f"../{schema_ref}"}
            if schema_ref
            else {"$ref": "#/components/schemas/CanonicalRecordFallback"}
        )
        paths: dict[str, Any] = {}
        for op in self._operations(context):
            success: dict[str, Any]
            if op.get("response_schema") is not None:
                inner = op["response_schema"]
                success = (
                    {"type": "array", "items": inner} if op.get("response_is_array") else inner
                )
            elif op["collection"]:
                success = {"type": "array", "items": record_schema}
            else:
                success = record_schema
            operation: dict[str, Any] = {
                "operationId": op["operation_id"],
                "summary": op["summary"],
                "tags": [target.universe],
                "responses": {
                    "200": {
                        "description": "Canonical knowledge projection.",
                        "content": {"application/json": {"schema": success}},
                    },
                    "404": {
                        "description": "No such canonical object in this universe.",
                        "content": {
                            "application/json": {"schema": {"$ref": "#/components/schemas/Error"}}
                        },
                    },
                },
            }
            if op["parameters"]:
                operation["parameters"] = op["parameters"]
            paths.setdefault(op["path"], {})[op["method"]] = operation

        payload = context.envelope(
            artifact_id=f"UCOS-URI-API-{target.path_slug.upper()}",
            title=f"{target.universe} — Realized Read API",
            document_format=API_DOCUMENT_FORMAT,
        )
        payload.update(
            {
                "openapi": OPENAPI_VERSION,
                "info": {
                    "title": f"{target.universe} Canonical Knowledge API",
                    "version": "1.0.0",
                    "description": (
                        "Read-only projection of the UKDA canonical knowledge store for "
                        f"the {target.universe} universe. Generated from canonical "
                        "knowledge; no write operation exists because realization "
                        "intelligence holds no authority to author knowledge "
                        "(UCKO-PRIN-0001)."
                    ),
                },
                "tags": [
                    {
                        "name": target.universe,
                        "description": f"Canonical knowledge homed in {target.universe}.",
                    }
                ],
                "paths": paths,
                "components": {
                    "schemas": {
                        "Invariant": {
                            "type": "object",
                            "required": ["cko_id", "kind", "authority", "statement"],
                            "additionalProperties": False,
                            "properties": {
                                "cko_id": {"type": "string"},
                                "kind": {"type": "string"},
                                "authority": {
                                    "type": "string",
                                    "enum": list(target.authorities),
                                },
                                "statement": {"type": "string"},
                            },
                        },
                        "Error": {
                            "type": "object",
                            "required": ["error", "code", "message"],
                            "additionalProperties": True,
                            "properties": {
                                "error": {"type": "string"},
                                "code": {"type": "string"},
                                "message": {"type": "string"},
                                "context": {"type": "object"},
                            },
                        },
                        "CanonicalRecordFallback": {
                            "type": "object",
                            "additionalProperties": True,
                        },
                    }
                },
                "x-ucos-realization": {
                    "target_id": target.target_id,
                    "target_seal": target.seal,
                    "record_schema": schema_ref,
                    "source_ckos": list(target.cko_ids),
                    "operation_count": len(self._operations(context)),
                },
            }
        )
        return payload

    # -- executable binding ---------------------------------------------------

    def _routes_module(self, context: GenerationContext) -> list[str]:
        target = context.target
        lines = self.provenance_comment(context, "#")
        lines += [
            '"""Read-only route table for the ' f"{target.universe} canonical knowledge universe.",
            "",
            "Framework-neutral: ROUTES maps (method, path template) to a handler that takes",
            "the canonical knowledge base and the resolved path parameters. Bind it to any",
            "HTTP layer without changing this file. Import is side-effect free; the canonical",
            "store is resolved lazily by load_base().",
            '"""',
            "",
            "from __future__ import annotations",
            "",
            "from typing import Any",
            "",
            f'UNIVERSE = "{target.universe}"',
            f'TARGET_ID = "{target.target_id}"',
            f'KNOWLEDGE_SEAL = "{context.intake.knowledge_seal}"',
            "SOURCE_CKOS = (",
        ]
        lines += [f'    "{cko_id}",' for cko_id in target.cko_ids]
        lines += [
            ")",
            "KINDS = (" + "".join(f'"{k}", ' for k in target.kinds) + ")",
            "LAYERS = (" + "".join(f'"{a}", ' for a in target.authorities) + ")",
            "INVARIANTS: tuple[dict[str, str], ...] = (",
        ]
        for inv in target.invariants:
            lines += [
                "    {",
                f'        "cko_id": "{inv.cko_id}",',
                f'        "kind": "{inv.kind}",',
                f'        "authority": "{inv.authority}",',
                f'        "statement": {inv.statement!r},',
                "    },",
            ]
        lines += [
            ")",
            "",
            "",
            "def load_base() -> Any:",
            '    """Resolve the canonical knowledge base lazily (no import-time side effects)."""',
            "    from engine.knowledge.seed import build_seed_base",
            "    from engine.knowledge.store import KnowledgeStore",
            "",
            "    store = KnowledgeStore()",
            "    return store.load() if store.exists() else build_seed_base()",
            "",
            "",
            "def _record(obj: Any) -> dict[str, Any]:",
            "    return obj.to_dict()",
            "",
            "",
            "def list_objects(base: Any, **_params: str) -> list[dict[str, Any]]:",
            '    """Every canonical object homed in this universe."""',
            "    return [_record(o) for o in base.by_universe(UNIVERSE)]",
            "",
            "",
            "def get_object(base: Any, *, cko_id: str, **_params: str) -> dict[str, Any]:",
            '    """One canonical object; raises KnowledgeNotFoundError when absent."""',
            "    if cko_id not in SOURCE_CKOS:",
            "        from engine.knowledge.errors import KnowledgeNotFoundError",
            "",
            "        raise KnowledgeNotFoundError(",
            '            "canonical object is not homed in this universe",',
            "            cko_id=cko_id,",
            "            universe=UNIVERSE,",
            "        )",
            "    return _record(base.require_object(cko_id))",
            "",
            "",
            "def list_kinds(_base: Any, **_params: str) -> list[str]:",
            '    """The knowledge kinds present in this universe."""',
            "    return list(KINDS)",
            "",
            "",
            "def list_objects_by_kind(base: Any, *, kind: str, **_params: str)"
            " -> list[dict[str, Any]]:",
            '    """Canonical objects of one knowledge kind."""',
            "    return [",
            "        _record(o)",
            "        for o in base.by_universe(UNIVERSE)",
            "        if o.kind.value == kind",
            "    ]",
            "",
            "",
            "def list_invariants(_base: Any, **_params: str) -> list[dict[str, str]]:",
            '    """The normative invariants this universe imposes."""',
            "    return [dict(entry) for entry in INVARIANTS]",
            "",
            "",
            "def list_layers(_base: Any, **_params: str) -> list[str]:",
            '    """The authority layers present in this universe."""',
            "    return list(LAYERS)",
            "",
            "",
            "ROUTES: dict[tuple[str, str], Any] = {",
        ]
        for op in self._operations(context):
            handler = op["operation_id"]
            lines.append(f'    ("{op["method"].upper()}", "{op["path"]}"): {handler},')
        lines += [
            "}",
            "",
            "",
            "def dispatch(method: str, template: str, base: Any, **params: str) -> Any:",
            '    """Invoke the handler bound to (method, template). Read-only by design."""',
            "    key = (method.upper(), template)",
            "    handler = ROUTES.get(key)",
            "    if handler is None:",
            "        from engine.knowledge.errors import KnowledgeNotFoundError",
            "",
            "        raise KnowledgeNotFoundError(",
            '            "no such route", method=method, template=template, universe=UNIVERSE',
            "        )",
            "    return handler(base, **params)",
            "",
            "",
            "__all__ = [",
            '    "UNIVERSE",',
            '    "TARGET_ID",',
            '    "KNOWLEDGE_SEAL",',
            '    "SOURCE_CKOS",',
            '    "KINDS",',
            '    "LAYERS",',
            '    "INVARIANTS",',
            '    "ROUTES",',
            '    "dispatch",',
            '    "load_base",',
        ]
        lines += [f'    "{op["operation_id"]}",' for op in self._operations(context)]
        lines.append("]")
        lines.append("")
        return lines


__all__ = ["API_DOCUMENT_FORMAT", "OPENAPI_VERSION", "ApiGenerator"]
