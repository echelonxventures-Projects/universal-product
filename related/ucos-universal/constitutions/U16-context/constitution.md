# U16 — Context Universe Constitution

| Field | Value |
|---|---|
| Universe ID | `U16-context` |
| Layer | L4 Foundation (runtime presence in L8 Gateway) |
| Domain | 01 Foundation |
| Steward | `ucos:org:platform-kernel-runtime` |
| Version | 0.1.0 (Draft) |
| Delivery phase | P0 |
| Depends on | U09 Identity, U10 Org & Tenant, U11 Party, U12 Geography, U13 Temporal, U14 Currency, U15 Localization, U66 Consent, U69 Risk (P2) |
| Depended on by | every runtime call (L7 law), U03 Policy (PDP context), U58 Composition (context resolution at compose time) |
| Master references | §7.6 (ContextEnvelope), §13.2 (request lifecycle), L7 |

> Context owns **the resolution, representation and propagation of the situation in which something happens**: who, for which tenant and blueprint, where (jurisdictions), when (`now` / `asOf`), in which language, currency and timezone, through which channel and device, at what risk, under which consent, and whether it is real or simulated. It produces the `ContextEnvelope`. It does not own any of the underlying facts. It *derives* from the universes that do.

---

## 1. Laws

| ID | Law | Enforcement |
|---|---|---|
| CTX-L1 | Every command, query, event, workflow step and AI call carries a resolved `ContextEnvelope`. | Gateway + command bus + SDK reject missing context (`CTX_MISSING`). |
| CTX-L2 | Context is resolved once at the edge (or at the workflow/trigger origin) and propagated unchanged. Downstream components may **narrow** it (e.g. add `purpose`) but never widen it. | Signed envelope; narrowing produces a child envelope linked to its parent. |
| CTX-L3 | Packs read context only through the SDK. They never re-derive jurisdiction, currency or locale from raw inputs. | Static rule + review. |
| CTX-L4 | `simulation=true` guarantees no external side effects: adapters switch to simulators, and outbound messages and payments are blocked. | Adapter layer checks the flag; certification test `ARCH-CTX-02`. |
| CTX-L5 | `asOf` (time travel) is a privileged capability, read-only unless `simulation=true`. | PDP rule. |
| CTX-L6 | Resolution rules are data (`ContextRule`), not code. | Resolver is generic; rules in registry. |

---

## 2. Ontology
- **`ContextEnvelope`** (value; master §7.6) — the resolved situation.
- **`ContextProfile`** — tenant/store/channel defaults (locale, currency, timezone, calendar, price list, catalog, theme).
- **`ContextRule`** — derivation rules, for example: `if channel=whatsapp then layout=conversational`, `if locale starts with ar then direction=rtl`, `if buyer.isMinor then audience=minor`, `if store.kind=dark-store then fulfilment.mode=quick-commerce`.
- **`ContextDimension`** registry (consolidates the 21 dimensions in master §7.6): each dimension declares owner universe, resolver, required (yes/no) and cache TTL.

| Dimension | Source universe | Resolver input |
|---|---|---|
| tenant, platformInstance | U10, U58 | host / API key / token `tid` |
| actor, roles, organization, onBehalfOf | U09, U10 | token |
| jurisdiction[] | U12 | role-specific locations (§5.2) |
| locale | U15 | user pref → account → Accept-Language → store → tenant |
| currency | U14 / U10 | store currency → user selection (display only) |
| timezone | U13 / U12 | user → device → store → tenant |
| time {now, asOf} | U13 | server clock; header for asOf |
| channel, device | U64, U09 | client id, user agent, device attestation |
| geo | U12 | delivery address / device location (consented) / IP (coarse) |
| risk | U69 | risk service (async-safe: default `unknown` band) |
| consent snapshot | U66 | party consents |
| purpose | U66 | set by caller per operation (narrowing) |
| simulation | U54 | workspace purpose / header |
| audience (minor, B2B, staff) | U11, U10 | derived rules |
| experiment assignments | U72 | feature flags / experiments |

---

## 3. Objects

### 3.1 `ContextEnvelope` (normative wire form)
JSON as in master §7.6, plus these fields:
- `v` (schema version);
- `parent` (hash of the parent envelope when narrowed);
- `sig` (Ed25519 signature by the gateway or cell key over the canonical JSON);
- `exp` (5 min, refreshed on long workflows by a re-resolve at step boundaries).

The envelope travels in header `ucos-context` (base64url) and in CloudEvents extension `ucoscontext`. Its size budget is ≤ 2 KB; large items are passed by reference (`consentSnapshotRef`).

### 3.2 `ContextProfile`
`{ id, scope: tenant|organization|store|channel|workspace, target, defaults: { locale, currency, timezone, calendar, priceList?, catalog?, theme?, ratePolicy? }, precedence }`. Precedence (normative, low to high): tenant → organization → store → channel → workspace → user preference → explicit request parameter (for display-only dimensions).

### 3.3 `ContextRule`
```yaml
id: ctx.rtl-for-arabic
when: "ctx.locale.language in ['ar','he','fa','ur']"     # CEL over envelope
set:  { "ui.direction": "rtl" }
priority: 100
owner: U15-l10n
```
Rules can only set **derived** keys under `ext.*` / `ui.*` or audience flags. Facts owned elsewhere, such as tenant or actor, cannot be overridden.

---

## 4. Contracts & APIs

- **Resolver (gateway filter)**, `resolve(request) → ContextEnvelope`:
  1. tenant from host or token;
  2. blueprint from tenant's active instance;
  3. actor from token;
  4. profiles merged by precedence;
  5. dimension resolvers run in parallel with deadlines (risk 30 ms, otherwise `unknown`);
  6. ContextRules applied;
  7. sign the envelope.
- **SDK:** `ctx := ucos.Context(r)`; `ctx.Jurisdictions()`, `ctx.Money(amount)` (currency-bound), `ctx.Now()` (respects `asOf`), `ctx.Narrow(purpose)`, `ctx.IsSimulation()`.
- **Workflow and trigger origin:** a workflow captures its starting envelope. Timer-fired steps re-resolve volatile dimensions (time, risk, consent), keep stable ones (tenant, actor/onBehalfOf), and record both.
- **Debug API (privileged):** `POST /v1/context:resolve` with a sample request returns the envelope and a resolution trace. Used by the Studio "preview as" feature (e.g. "view storefront as a buyer in Dubai, ar-AE, on iOS").
- **Errors:** `CTX_MISSING`, `CTX_SIGNATURE_INVALID`, `CTX_EXPIRED`, `CTX_WIDENING_FORBIDDEN`, `CTX_ASOF_FORBIDDEN`, `CTX_TENANT_MISMATCH`.

---

## 5. Rules & Algorithms

### 5.1 Resolution order & determinism
Given the same request, profiles and rules version, resolution is deterministic. The resolution trace lists the source of every dimension, e.g. `locale: ar-AE (source: user-preference)`.

### 5.2 Jurisdiction roles (normative)
The envelope holds `jurisdictions` as a **map by role**, not a flat list:
```json
"jurisdiction": {
  "actor":        ["ucos:jur:AE", "ucos:jur:AE-DU"],
  "buyer-delivery":["ucos:jur:AE", "ucos:jur:AE-DU"],
  "seller":       ["ucos:jur:IN", "ucos:jur:IN-MH"],
  "data-storage": ["ucos:jur:AE"],
  "store":        ["ucos:jur:AE"]
}
```
Consumers declare which roles they use. Tax uses the supply rules in U31, privacy uses `actor` + `data-storage`, consumer law uses `buyer-delivery`. This resolves the master §7.6 ambiguity of a flat `jurisdiction[]`.

---

## 6. Security & Compliance
- The envelope is signed by cell keys (rotated every 30 days via KMS). Verification is local.
- It contains no raw PII: actor and party appear as ids, geo is coarse (place ids), and IP is hashed.
- PDP policies use the context attributes directly.
- Compliance: evidence that purpose limitation is enforced (`purpose` recorded on every access to purpose-tagged data), and the simulation isolation proof.

## 7. Validation & Reuse
- Packs consume context only via the SDK.
- New dimensions require an amendment to this universe (registry entry + resolver) at authority level 4.
- Certification:
  - `ARCH-CTX-01`: the pack never parses `Accept-Language` or IP itself (static scan);
  - `ARCH-CTX-02`: simulation side-effect test (every adapter registered with a simulator).

## 8. Gaps & Evolution
```prolog
gap(no_context_profile, T)         :- tenant(T), not context_profile(T, tenant).
gap(store_profile_missing, S)      :- store(S), currency_differs_from_tenant(S), not context_profile(S, store).
gap(adapter_without_simulator, A)  :- adapter(A), not simulator_for(A).
gap(dimension_without_resolver, D) :- context_dimension(D), required(D), not resolver(D).
```
**Evolution:** spatial and XR context (room, anchor) and agent-society context (agent team, mission) are added as new dimensions.

## 9. AI
AI calls carry the envelope. The AI gateway uses `jurisdiction.data-storage` and the tenant AI policy to pick the model region. Agents receive a narrowed envelope (`actor = agent`, `onBehalfOf = user`, plus `purpose`).

## 10. Operations
- **Signals:** `context_resolve_latency_ms` (p99 target < 3 ms excluding risk), `context_dimension_fallback_total{dimension}`, `context_signature_failures_total` (alert on > 0), `simulation_blocked_side_effects_total`.
- **Runbook:** signing key compromise means rotating the key, invalidating envelopes older than the rotation, and forcing re-resolve.

## 11. UI
- **Views:** `context.preview-as` (Studio: choose tenant, store, locale, currency, device, persona and asOf, then preview the generated UI), `context.trace` (developer tool).
- End users see context as locale, currency and delivery-location pickers. Changes write user preferences (U11) and re-resolve.

## 12. Scale
Resolution runs on every request: about 1M resolutions/s per large cell. Profiles and rules are cached in gateway memory, with invalidation by event. Tier T0, embedded in the gateway.

## Appendix
- **B. Amendments:** master §7.6 `jurisdiction: JurisdictionRef[]` becomes a role-keyed map (§5.2 above).
- **C.** 0.1.0.

## Appendix D — Frame dimension (amendment A-27, from U77)
- New required dimension `frame` = `{ reality, body, spatialFrame, timeScale, calendarSystem }`. It is resolved as: request header (privileged) → workspace (simulation/virtual workspaces) → tenant default → `ucos:frame:earth-physical`.
- `simulation: boolean` is kept for backward compatibility, but it is now derived: `simulation = frame.reality.kind ∈ {simulated, hypothetical}`.
- Narrowing may move from `physical` into a branch reality (what-if), but never the reverse inside one request.

## Appendix P1 — Phase 1 behaviour without later-phase dependencies
- **U69 Risk (Phase 2):** the `risk` dimension resolves to `{score: null, band: unknown}`. Policies MUST treat `unknown` like `medium` for step-up decisions in Phase 1 (platform policy default).
