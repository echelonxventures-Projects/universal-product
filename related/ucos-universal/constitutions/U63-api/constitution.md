# U63 — API Universe Constitution

| Field | Value |
|---|---|
| Universe ID | `U63-api` |
| Layer | L9 Integration |
| Domain | 09 Platform |
| Steward | `ucos:org:platform-api` |
| Version | 0.1.0 (Draft) |
| Delivery phase | P1 (REST/GraphQL generation, gateway, keys, rate limits, dev portal basics), P3 (SDK generation, API products), P4 (MCP server for external agents) |
| Depends on | U57 Capability (commands/queries), U04 Meta (schemas), U03 Policy (PEP), U09 Identity (OAuth clients), U16 Context, U28 Entitlement (API plans, P2), U61 Event (webhooks via U62), U13 Temporal (see TEMPORAL-BINDING-MATRIX) |
| Depended on by | all clients: renderers (L10), partners, tenant developers, connectors, agents |
| Master references | §15.1–§15.3 (conventions, errors, generic object API), §12.1 (SDK generation) |

> API owns **the external contract surface of every blueprint**: API definitions generated from capability manifests (REST/OpenAPI 3.1, GraphQL subgraphs, gRPC for internal, MCP tools for agents), API products (bundles exposed to partners with plans), API clients and credentials, rate limits & quotas, versioning/deprecation, the gateway configuration, and the developer portal. It owns no business behaviour.

---

## 1. Laws

| ID | Law | Enforcement |
|---|---|---|
| API-L1 | Public API surface is generated from registered commands/queries/object types; hand-written endpoints are not permitted except kernel/system endpoints. | Gateway routes only from generated config; CI diff check. |
| API-L2 | Conventions of master §15.2 (paths, commands `:verb`, idempotency, ETags, problem+json, cursors, RateLimit headers) are mandatory. | API linter (Spectral ruleset `ucos-api`). |
| API-L3 | Breaking changes only in a new major version; deprecations announced with `Deprecation`/`Sunset` headers ≥ 6 months (≥ 12 months for T0/T1 APIs). | Compatibility checker on OpenAPI diff; Governance class. |
| API-L4 | Every request is authenticated (OAuth2/OIDC, mTLS, signed API key for low-risk read) and authorised by the PEP; anonymous APIs are explicitly declared. | Gateway config validation. |
| API-L5 | Rate limits and quotas are defined per API product × plan × principal, with fair-share per tenant. | Gateway enforcement. |

## 2. Objects
- **`APIDefinition`** `{ id, blueprint, version (major), styles: [rest, graphql, grpc, mcp], openapi: generated ref, graphqlSDL ref, protos ref, mcpTools ref, operations: [{operationId (= universe:Command|Query), method/path, auth, scopes, rateClass, idempotencyRequired, public: bool, deprecated?}] }`
- **`APIProduct`** `{ id, tenant, name, operations subset, plans: [{name, quota (requests/period), rate (rps), price (via Entitlement)}], audience: internal|partner|public, docs, terms }`
- **`APIClient`** `{ id, tenant, owner (org/developer), type: confidential|public|machine, grantTypes, redirectUris, scopes, products subscribed, credentials: [client secret hash | mTLS cert | private_key_jwt jwks], status }`
- **`RateLimitPolicy`** `{ class, limits: {perPrincipal, perTenant, burst}, algorithm: token-bucket (GCRA), scope: cell }`
- **`MCPToolDefinition`** (generated) `{ name (snake), description (from manifest, localised en), inputSchema (JSON Schema), sideEffectClass, requiredAuthority, confirmationRequired }`

## 3. Generation (normative)
```text
for each capability in blueprint:
  for each command C: REST POST /v1/{slug}/{collection}/{id}:{verbCamel}  (or POST collection for create)
                      GraphQL mutation {slug}{Command}
                      MCP tool {slug}_{command_snake} if manifest.ai.tools includes it
  for each query Q:   REST GET (resource/collection), GraphQL query field, MCP tool (read)
  object types → schemas (JSON Schema → OpenAPI components; GraphQL types with field-level @policy directive)
  errors → problem types per error code registry
outputs: OpenAPI 3.1 (per universe + merged), GraphQL subgraph SDL per universe (federation v2), gateway route config, SDKs (TS, Kotlin, Swift, Python, Go) via U59 Generation
```

## 4. Commands, Queries, Events, APIs
Commands: `GenerateAPI(blueprint)` (on activation), `PublishAPIProduct`, `RegisterClient`, `RotateClientSecret`, `SubscribeClientToProduct`, `DeprecateOperation(sunset)`.
Queries: `GetOpenAPI(blueprint, version, audience)`, `GetGraphQLSchema`, `UsageFor(client, range)`.
Events: `api.definition.generated`, `api.client.registered`, `api.operation.deprecated`, `api.quota.exceeded`.
```text
GET /v1/api/openapi.json?audience=partner     GET /v1/api/graphql/schema
POST /v1/api/clients     POST /v1/api/clients/{id}:rotate-secret     POST /v1/api/products
GET /v1/api/usage?client=&from=&to=
```

## 5. Security & Compliance
OAuth 2.1 (PKCE for public clients, DPoP or mTLS sender-constraining for high-value APIs), audience-bound tokens, scope = permission strings, BOLA/IDOR protection by PDP on every resource, input validation from schemas at gateway, response field masking per obligations, OWASP API Top 10 tests generated per API (security gate), abuse detection (U69). Open Banking/PSD2-style consent APIs reuse U66 consents (future).

## 6. Gaps
```prolog
gap(operation_without_policy, O)  :- api_operation(O), not policy_covers_action(O).
gap(public_op_without_rate_limit, O) :- api_operation(O), public(O), not rate_class(O, _).
gap(sdk_outdated, B, L)           :- active_blueprint(B), sdk(B, L, V), V != api_version(B).
gap(sunset_soon_with_traffic, O)  :- deprecated(O), sunset_within_days(O, 30), traffic_7d(O, N), N > 0.
```

## 7. AI
MCP server exposes generated tools to external agents (P4) with OAuth + delegation; AI-generated API usage examples in docs (reviewed); anomaly detection on API usage.

## 8. Operations, UI, Scale
Signals: `api_requests_total{op,status}`, `api_latency_ms{op}` (gateway p99 overhead < 5 ms), `rate_limited_total`, `deprecated_calls_total{client}`. Views: developer portal (Backstage-fed: API reference, try-it sandbox, SDK downloads, changelog, webhooks), `api.product.manager`, `api.client.console` (credentials, usage), `api.deprecation.tracker`. Scale: 50k–1M rps per cell at the gateway (Envoy), config hot-reloaded per blueprint activation. T0.

## Appendix
- **C.** 0.1.0.

## Appendix P1 — Phase 1 behaviour without later-phase dependencies
- **U28 Entitlement and U62 Integration:** specified for Phase 1. API plans and quotas come from U28. Tenant outbound webhooks are delivered by U62.
