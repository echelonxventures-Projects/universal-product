# U64 — UI, App & Channel Universe Constitution

| Field | Value |
|---|---|
| Universe ID | `U64-ui` |
| Layer | L10 Experience |
| Domain | 06 Experience |
| Steward | `ucos:org:experience-platform` |
| Version | 0.1.0 (Draft) |
| Delivery phase | P1 (UI meta-model, web renderer, storefront + admin portal shells, design system v1), P3 (Studio designers, mobile renderer, journeys, theming at scale), P4 (chat/voice/agent renderers) |
| Depends on | U04 Meta (object types), U57 Capability (manifest ui sections), U15 Localization, U03 Policy (field obligations), U16 Context (channel, locale, direction), U43 Asset (brand assets), U63 API (data access), U72 Analytics (UI telemetry), U13 Temporal (see TEMPORAL-BINDING-MATRIX) |
| Depended on by | all portals and storefronts; Builder Studio itself is built on this universe (dogfooding) |
| Master references | §22–§25 (experience architecture, design system, IA, wireframes), §22.2 (ViewDefinition), §23.2 (tokens) |

> UI owns **experiences as metadata and the renderers that turn them into interfaces**: ViewDefinitions, Layouts, Components (abstract), Journeys, Portals/Apps (navigation shells), Themes & design tokens, Channels (web, iOS, Android, desktop, kiosk/POS, TV, chat/WhatsApp, voice, agent UI), and channel capability fallbacks. Renderers are platform code; screens are data.

---

## 1. Laws

| ID | Law | Enforcement |
|---|---|---|
| UI-L1 | Screens are ViewDefinitions; no tenant-specific or capability-specific hand-coded pages in renderers. Custom visual widgets are allowed only as registered Components (extension point `ui.widgets`) shipped in ui-packs. | Renderer loads only registry components; CI rule. |
| UI-L2 | All text via i18n keys / LocalizedText; layout supports RTL; WCAG 2.2 AA is a certification gate. | L10N-L1; `A11Y-*` gates. |
| UI-L3 | Field visibility/masking/editability follows PDP obligations at render time and is re-enforced server-side; UI never relies on hiding for security. | Renderer reads obligations; APIs enforce independently. |
| UI-L4 | Themes change tokens only (master §23.2); contrast validated; components are not forked per tenant. | Theme validator. |
| UI-L5 | Consumer-facing views follow honest-design rules (no pre-ticked consents, no fake urgency/scarcity, clear totals). | View lint rules + compliance review for commerce views. |

## 2. Objects
- **`ViewDefinition`** — master §22.2 (types: list, detail, form, board, calendar, map, timeline, dashboard, wizard, chat, document, graph-canvas); `variants` per channel/breakpoint; `dataBindings` (queries/commands via API), `actions` (commands with confirm/step-up obligations), `validation` (schema + decisions), `analytics`, `a11y` hints.
- **`Component`** `{ id, abstract role (Field, Collection, Action, Media, Map, Calendar, Chart, …), props schema, renderer implementations: {web: npm ref, mobile: rn ref, voice: intent mapping, chat: card template}, a11y contract, fallback }`
- **`Layout`** (page templates/regions) and **`Journey`** `{ id, steps: [{view, entryCondition, exit transitions}], analytics funnel, resumable: bool }`.
- **`Portal` / `App`** `{ id, audience, navigation (IA tree referencing views), auth requirements, theme, domains/app ids, channels, featureFlags }` — e.g. Console IA (master §24.1), seller hub, storefront.
- **`Theme`** `{ tokens (master §23.2), assets (logo, favicon, app icons), fonts, modes }` per Brand (U10).
- **`ChannelProfile`** `{ channel, capabilities matrix (master §22.4), renderer, constraints (char limits, card types), fallbacks }`.
- **`MobileAppBuild`** (P3) `{ app, platform: ios|android, bundle id, version, theme, feature set, store listing, release track }` — built by Generation (U59) from the same metadata.

## 3. Rendering model
- **Web:** Next.js runtime that fetches compiled view bundles (JSON) per blueprint/tenant/locale (CDN-cached, hash-addressed); server-side rendering for storefront SEO; component library in React; data via GraphQL federation/BFF.
- **Mobile:** React Native/Expo shell interpreting the same view JSON; offline cache for selected views; OTA metadata updates (no store release for screen changes; store release only for shell/native module changes).
- **Chat/WhatsApp/Voice:** conversational renderer maps views to message flows (forms → slot filling; lists → carousels/top-N; confirmations explicit).
- **Agent UI:** views expose structured cards + MCP tool affordances.
- View compilation step: resolves components, permissions skeleton, i18n keys, theme → per-locale bundles; validated (a11y static checks, broken bindings).

## 4. Commands, Queries, Events, APIs
Commands: `ProposeView`/`PublishView` (governed; tenant views standard/normal), `DefineJourney`, `DefinePortal`, `PublishTheme`, `RegisterComponent` (ui-pack publish), `BuildMobileApp` (P3).
Queries: `CompiledView(viewId, tenant, locale, channel)`, `PortalManifest(portal, principal)` (navigation filtered by permissions), `PreviewAs(ctx)` (with U16).
Events: `ui.view.published`, `ui.theme.published`, `ui.portal.published`, UI telemetry → U72 (`ui.view.rendered`, `ui.action.clicked`, sampled, consent-aware).
```text
GET /v1/ui/views/{id}/compiled?locale=&channel=     GET /v1/ui/portals/{id}/manifest
POST /v1/ui/views     POST /v1/ui/journeys     POST /v1/ui/themes     POST /v1/ui/portals
```

## 5. Gaps
```prolog
gap(command_without_view, C)      :- command(C), human_invocable(C), in_blueprint(C), not view_action_for(C).
gap(object_without_detail_view, T):- object_type(T), in_blueprint(T), user_facing(T), not view(T, detail).
gap(a11y_violation, V)            :- view(V), axe_critical_violations(V, N), N > 0.
gap(rtl_unverified, V)            :- view(V), tenant_rtl_locale(_), not rtl_snapshot_pass(V).
gap(theme_contrast_fail, Th)      :- theme(Th), contrast_failures(Th, N), N > 0.
```

## 6. Security & Compliance
CSP strict on web renderers, no third-party scripts except registered analytics/payment SDKs; clickjacking protection; PSP-hosted payment fields; accessibility law (EN 301 549, ADA, RPwD Act India); dark-pattern rules (CCPA India guidelines 2023, EU DSA/UCPD, FTC).

## 7. AI
View drafting from intent ("a page to approve refunds over ₹5k") → ViewDefinition proposal; alt-text and copy suggestions; UX analytics insights (drop-off explanations); generative personalisation limited to approved slots.

## 8. Operations, UI, Scale
Signals: `lcp_ms{portal,channel}` (storefront p75 < 2.5 s), `inp_ms`, `cls`, `js_errors_total`, `view_render_errors_total`, `a11y_violations_total`. Studio views: UI/Journey designer (master §12.4), theme designer, preview-as. Scale: view bundles on CDN; renderer stateless; millions of sessions. T1 (storefront T0-like with static fallbacks).

## Appendix
- **A.** Flutter renderer (alternative) — evaluate only if RN performance insufficient for POS/kiosk.
- **D. Attribute definitions (A-74).** `ViewDefinition { id, version: string, type: list|detail|form|board|calendar|map|timeline|dashboard|wizard|chat|document|graph-canvas, objectType?: string, variants: [{channel, breakpoint, layout}], dataBindings: [{query|command, params}], actions: [{command, confirm, obligations}], fields: [{path, component, readOnly}], a11y: {landmarks, focusOrder}, localeKeys: [string], status: draft|published|deprecated }`
- **C.** 0.1.0.
