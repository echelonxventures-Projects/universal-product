# LUXORA — the complete remaining todo list

> Measured on 2026-10-21. Since then: routes and console screens moved into their domains (21 November), and the
> go-live work of AMD-0051 (24 November). For what still stands in the way of real customers on an install, run
> `npm run preflight`.

Everything below is read out of the project's own registers, not invented: `_registry/roadmap.json`
(the build path, the decisions and the gap register), `_registry/domains.json` (the 26 laws, the 12
kernel parts, the 47 domains and their build status), `_registry/business-domains.json` (the 57 business
domains and what each owns), `_registry/classification.json` (the concept register),
`lib/seed/capabilities.json` (the capability catalogue), `GLOBAL_MASTER.md` (the adopted design and its
nine phases), `scripts/coverage-matrix.js` and `scripts/domain-map.js` (the two gates that decide
whether anything is mixed), and the live gates themselves.

**The governing rule for everything below: nothing is mixed.** Every domain — Offer, Identity, Product,
Services, Shipping, Payment gateway, Billing, Audit, SEO and all the rest — stands alone, complete in
itself: its own engine, its own tables, its own state machines, its own capabilities, its own routes,
its own console screens, its own storefront pages, and its own document that explains it end to end
(overview, switches, architecture, data model, API reference, process flows, data flow, user
interface, user flows) plus a manual section for every kind of user who touches it.

**State as measured on 2026-10-21:** 32 build steps — 9 done, 3 in progress, 20 planned. 30 recorded
gaps — 21 open, 9 closed. 26 laws — 6 enforced, 10 partial, 10 planned. 12 kernel parts — 8 built,
4 partial. 47 constitutional domains — 35 partial, 12 designed. 57 business domains — 1 fully
documented, 56 with 208 sections still unwritten. 32 platform types — 7 fully covered, 25 still
requesting 30 capabilities that do not exist.

---

## PART ONE — Make each domain stand alone (the structural work)

This is the part that answers "Offer means complete offers, discounts, all related — nothing mixed",
applied to all 57 business domains. The project already has the mechanism: `_registry/business-domains.json`
declares what every domain owns, `scripts/domain-map.js` reads the artifacts out of the code and proves
each is owned exactly once, and `test/domain-map.js` holds a **ratchet** on the debts of mixing. The
ratchet can only fall.

### 1.1 Where the mixing actually is, measured

| Debt | Count | What it means |
|---|---|---|
| `routesInSharedFile` | **839** of 875 | Almost every route still lives in the one 9,342-line `lib/api.js`. Only `lib/routes/offer.js` (36 routes) is in a file of its own. |
| `screensInSharedScript` | **88** of 94 | Almost every store console screen still lives in the one 3,076-line `public/js/admin.js`. Only `public/js/admin/offer.js` is in a file of its own. |
| `mixedConsoleGroups` | **14** | Fourteen console groups each mix two or three domains. |
| `routesUndescribed` | **722** of 875 | 722 routes have no description, so the API reference of 56 domains says nothing about them. |
| `domainsUndocumented` | **56** of 57 | Only Wallets is complete. |

The fourteen mixed console groups, each of which must be split so one group belongs to one domain:

| Console group | Domains mixed into it |
|---|---|
| Identity | identity, stores, access |
| Access | access, identity |
| Policy | access, rules |
| Configuration | kernel, rules, stores |
| Provenance | stores, catalog |
| Capabilities | modules, stores |
| Extension | integration, modules |
| Billing & Payment | platform_billing, payments, settlement |
| Recurring | platform_billing, subscriptions |
| Supply | supply, business_operations |
| Oversight | risk, audit, knowledge |
| Telemetry | analytics, runtime |
| Insight | analytics, kernel, catalog |
| Constitution Ω∞ | knowledge, kernel |

### 1.2 The standard every domain must meet

The pattern is already proven by the **offer** domain, extracted in the most recent commit
("the Offers domain in files of its own"). Every domain must reach this shape:

| Artefact | The rule | Today |
|---|---|---|
| `lib/<domain>.js` | the domain's engine, and nothing else's | 18 of 57 domains have a file by their own name |
| `lib/routes/<domain>.js` | the domain's routes, and only its routes | 1 of 57 |
| `public/js/admin/<domain>.js` | the domain's console screens, and only its screens | 1 of 57 |
| `lib/seed/<domain>.json` | the domain's vocabularies, capabilities and state machines | partial |
| `schema.sql` | the domain's tables, grouped and declared by the domain that owns them | 298 tables, mixed across one file |
| `docs/domains/<domain>.md` | the domain's own complete document | 57 of 57 exist but 56 are incomplete |
| `docs/source/<domain>.md` | what only a person can say: its flows and its manuals | 1 of 57 |

The route extraction is mechanical once the shape is understood: `lib/routes/offer.js` receives the
shared HTTP kit as `kit` and exports `{ domain: "offer", routes(kit) }`. The console extraction mirrors
it in `public/js/admin/offer.js`, registering screens with `screen("key", {...})`.

### 1.3 The order to split in

Split the domains that are largest and most mixed first, because each extraction teaches the next one
and the ratchet proves the progress. **Every extraction must leave the gates green** — same routes,
same responses, same tables, same screens; only the file they live in changes.

- [ ] **Tier 1 — the money and the offer spine.** `payments`, `billing`/`platform_billing`, `settlement`, `wallet`, `fintech`/`financial_services`, `tax`. These share the "Billing & Payment" and "Recurring" console groups and the largest cluster of routes.
- [ ] **Tier 2 — the catalogue spine.** `catalog`, `product_content`, `product_options`, `inventory`, `pricing`, `currency`, `supply`. "Provenance" mixes stores and catalog.
- [ ] **Tier 3 — the transaction spine.** `cart`, `order`, `returns`, `subscriptions`, `affiliate`, `advertising`, `price_discovery`, `trade`, `marketplace`, `shipping`, `mobility`, `services`, `health`, `digital_goods`, `made_to_order`, `business_operations`.
- [ ] **Tier 4 — the platform spine.** `identity`, `access`, `customers`, `stores`, `modules`, `rules`, `kernel`, `runtime`, `communication`, `support`, `engagement`, `reviews`, `search`, `seo`, `localisation`, `consoles`, `analytics`, `experiments`, `risk`, `compliance`, `audit`, `security`, `ai`, `integration`, `geography`, `knowledge`.
- [ ] **Each extraction:** move the routes to `lib/routes/<domain>.js`; move the console screens to `public/js/admin/<domain>.js`; move the tables into the domain's own section of the schema; declare all of it in `_registry/business-domains.json`; then lower `_registry/business-baseline.json` with `node test/domain-map.js --update`.
- [ ] **End state:** `routesInSharedFile` → 0, `screensInSharedScript` → 0, `mixedConsoleGroups` → 0. `lib/api.js` becomes a thin HTTP kit that assembles the domain route files, and `public/js/admin.js` becomes a thin shell that loads the domain console files. Neither should know any business.

### 1.4 Two schema sources have already drifted

`schema.sql` is the reference snapshot; `lib/db.js` carries its own inline copy of the schema. They
have diverged: **27 tables exist only in `schema.sql`** (`k_nodes`, `k_events`, `k_kinds`,
`k_hierarchies`, `k_versions`, `k_changes`, `k_shapes`, `k_coord_systems`, `k_declarations`,
`k_placements`, `k_node_states`, `k_assignments`, `affiliates`, `affiliate_clicks`,
`affiliate_conversions`, `affiliate_networks`, `affiliate_payouts`, `affiliate_tiers`,
`commission_rules`, `shipping_providers`, `shipping_quotes`, `package_tracking`,
`sitemap_config`, `sitemap_entries`, `sitemap_files`), and **one exists only in `lib/db.js`**
(`cart_items_v2`).

Most of those are real tables the runtime creates — `lib/kernel.js` creates the `k_*` tables,
`lib/affiliate.js` the `affiliate*` tables, `lib/shipping.js` the shipping quotes, `lib/sitemap.js`
the sitemap tables. `scripts/schema-dump.js` exists to regenerate the snapshot from a boot, and
`test/security.js` fails when the snapshot is stale.

- [ ] Decide the single source of truth for the schema. The clean answer, and the one that supports "nothing is mixed": **each domain owns its own table declarations**, and the schema is composed from the domains rather than hand-maintained in two places.
- [ ] Either way, regenerate `schema.sql` (`npm run schema`) and make `test/security.js` fail on the drift that is present today.
- [ ] `cart_items_v2` — determine whether it is a live table, a migration leftover, or dead code. It exists in exactly one of the two sources and in neither domain's declaration.

---

## PART TWO — Make each domain's document complete and standalone

`scripts/domain-docs.js` generates every domain document from the code plus hand-written
`docs/source/<domain>.md`. What the code says is read from the code; what only a person can say is
written once and cannot drift. **Each document must stand alone** — a reader who opens `docs/domains/offer.md`
must learn everything about offers without opening another domain's document.

### 2.1 The ten sections every domain document must carry

The generator already emits them, in this order:

| Section | From | Complete? |
|---|---|---|
| Overview — what the domain is for, its foundation, who uses it | `_registry/business-domains.json` | generated for all 57 |
| Switches and settings — each capability, its parameters, and where it is switched | the capability catalogue | generated |
| Architecture — the module, its dependencies, its place in the platform | the code | generated |
| Data model — every table the domain owns, column by column | `schema.sql` | generated |
| API reference — every route the domain owns, with its description | `lib/api.js` and `lib/routes/*.js` | generated, but **722 routes have no description** |
| Process flows — every state machine the domain owns, as a Mermaid diagram | `lib/seed/states.json` | generated |
| Data flow — a Mermaid flow of the domain's data | the code | generated |
| User interface — the domain's console screens and storefront pages | the console and page files | generated |
| **User flows** — how the flow is meant to go | `docs/source/<domain>.md`, `## Flows` | **56 unwritten** |
| **Manuals** — one section per user type | `docs/source/<domain>.md`, `## Manual: <user>` | **152 unwritten** |

### 2.2 The documentation work, precisely

- [ ] Write `## Flows` for all 56 domains that lack one. This is how the flow is *meant* to go — the parts the code cannot say.
- [ ] Write `## Manual: <user>` for all 152 outstanding domain/user pairs.
- [ ] Give all 722 undescribed routes a description — the comment above each handler is what the API reference prints. This is also what makes `routesUndescribed` fall to 0.
- [ ] Move `USER_MANUAL.md` from hand-written to generated, and add it to the same check that guards `docs/domains/` (`GAP-24`).
- [ ] Each domain document must cross-reference only what it needs, never duplicate another domain's detail — the document is generated from the owning code, so duplication cannot occur by construction.

### 2.3 The manuals, by user type

Ten user types, and each manual gathers only the domains that user touches:

| User type | Domains they use | Manual sections |
|---|---|---|
| Store administrator | every store-level domain — 50 of the 57 | 50 |
| Platform administrator | 29 — the platform console, plus the platform-owned domains | 29 |
| Shopper | 27 — identity through storefront, including cart, order, returns, payments, wallet | 27 |
| Store staff | 19 — the daily work of the shop floor | 19 |
| Seller | 13 — the catalogue they sell, pricing, offers, settlement | 13 |
| Developer | 7 — identity, payments, security, integration, kernel, knowledge, runtime | 7 |
| Guest | 5 — identity, cart, engagement, storefront, search | 5 |
| Partner or affiliate | 2 — offer, affiliate | 2 |
| Driver or rider | 2 — shipping, mobility | 2 |
| Practitioner | 2 — services, health | 2 |
| | **156 sections in total** | **152 still unwritten** |

The 156 is the sum of every domain's user list; 152 are unwritten because Wallets is the only complete
domain, and it carries 4 manual sections that are written. Only **Wallets** is complete today — it has
all ten sections filled, and it is the exemplar to copy.

---

## PART THREE — The gates that are red right now

The build is not shippable today. Four checks fail and the working tree has 39 modified files plus
three untracked ones.

| Gate | Result now | What it wants |
|---|---|---|
| `npm test` → `test/registry-gate.js` | 62 passed, **2 failed** | `lib/giftcards.js` and `lib/seed/giftcards.json` have no home in `_registry/codebase.json`. Every code file must map to one owning domain. |
| `npm test` → `test/audit-gate.js` | 1 passed, **2 failed** | `lib/goip.js · gift_card` added a branch (0 → 1) and `lib/goip.js · GOIP_HANDLERS` grew 40 → 42 lines. The ratchet forbids new hard-coding; it does not forgive it. |
| `npm test` → `test/domain-map.js` | 34 passed, **1 failed** | `docs/domains/offer.md` and `docs/domains/storefront.md` were hand-edited and no longer match the generator. |
| `node scripts/domain-docs.js --check` | **stale** | The same two files. |

- [ ] Map `lib/giftcards.js` and `lib/seed/giftcards.json` in `_registry/codebase.json` — gift cards belong to the **Offers** domain, which already declares `lib/giftcards.js` in its `owns.files`.
- [ ] Re-seed the gift-card work out of `lib/goip.js` so the `gift_card` branch and the `GOIP_HANDLERS` constant return to baseline size. Do **not** re-baseline `scripts/audit-baseline.json` to hide it.
- [ ] Run `node scripts/domain-docs.js` to regenerate the two documents. Hand edits to generated files are always lost.
- [ ] Decide what to do with the 39 modified files and 3 untracked files (`lib/giftcards.js`, `lib/seed/giftcards.json`, `test/offer.js`) — coherent gift-card work in flight. Finish and commit it behind a registered amendment, or stash it.
- [ ] Record the result as **AMD-0039**, and point any closed gap at it — the gate refuses a closed gap that names no amendment.

**Note on the registry seal.** `npm run registry` fails with `Error: disk I/O error` when it uses the
default database. That is not a code defect: `lib/db.js` opens `data/luxora.db`, and the repository sits
in an iCloud-synced Desktop folder whose file locking breaks SQLite. Running the same compile with
`LX_DB=/tmp/reg-compile.db node _registry/compile.js --gate` works and reports the real failure. See
item 6.1 — moving the repository out of iCloud is the actual fix.

---

## PART FOUR — The 20 unenforced laws (LAW-026: a law without a check is not finished)

This is the constitutional spine, and it is what `_registry/register-baseline.json` counts as
`lawsNotEnforced: 20`. The count may only fall.

### 4a. The 10 planned laws — no enforcement at all

| Law | What it demands | The check that must exist |
|---|---|---|
| LAW-009 Dependency Law | Identity → Knowledge → Relationships → Context → Policy → Trust → Projection; no cycles, no mutual ownership, no cross-domain state mutation | A test that reads the domain graph and fails on a cycle |
| LAW-010 Runtime Responsibility | The constitution defines truth, domains manage it, the runtime derives reality, agents execute, applications consume | A test that fails when a domain's code performs another domain's write |
| LAW-014 Infinite Extensibility | Every domain assumes no Earth, country, calendar, unit, language or direction | Extend the hard-coding audit to the domain layer |
| LAW-015 Technology Agnostic | No vendor, database, cloud or framework in the domain layer; each is an adapter chosen by configuration | A test that fails on a vendor name in `lib/` outside the adapter files |
| LAW-016 Contextual Distribution | Configuring a place projects what applies there, inherited down the place hierarchies | A test that a place inherits its country's rules and overrides them |
| LAW-017 Platform-Owned Master Data | Platforms select master data through views and never copy it | A test that no tenant-scoped copy of a master entity exists |
| LAW-018 Selection From Owners | Every choice offered anywhere is a selection from the domain that owns the subject | A test that every console picker reads from its owner's vocabulary |
| LAW-022 Bounded Agents | An agent is a party with declared permissions, scope, budget and audit; never exceeds its principal | A test that an agent's grants are a subset of its principal's |
| LAW-023 Security Floor | Policy may tighten the baseline but never weaken it | A test that no tenant configuration can lower the floor |
| LAW-025 Packages Compose | Packages compose domains into editable platforms; overlays survive upgrades | A test that an overlay survives a package upgrade |

**LAW-007 and LAW-010 are the two that bear directly on "nothing is mixed".** LAW-007 says no concept
exists without an owner, no capability without a boundary, no boundary without a contract — and the
domain map already proves every artifact has exactly one owner. LAW-010 says domains manage truth and
nothing else — which is what the file split in Part One enforces mechanically.

### 4b. The 10 partial laws — each with a named remainder

| Law | Enforced today by | What is missing |
|---|---|---|
| LAW-004 Constitutional Governance | the gate and the amendment record | every capability, change and autonomous action governed |
| LAW-005 Explainability | `lib/audit.js` standard contract | every action answers what, why, who authorised it, which policy, what evidence, what confidence, what alternatives |
| LAW-006 Configuration Over Code | `scripts/audit-hardcoding.js`, `test/audit-gate.js` | fully metadata-driven — the ratchet stands at 51 branches / 87 fallbacks, not zero |
| LAW-008 Independent Authorities | `test/places.js`, `test/stores.js` | `schema.sql` still carries 21 `DEFAULT 'US'` / `DEFAULT 'USD'` columns and country columns on `brands`, `warehouses`, `suppliers`, `dark_stores` |
| LAW-012 Generated Platform | `_registry/project.js` documentation | data models, APIs, interfaces, workflows, state machines, reports, dashboards, permissions, integrations, SDKs and tests all generated |
| LAW-013 Registry First | `lib/canonical.js` search | everything discoverable — `GAP-25`: search does not cover universes or corpus documents |
| LAW-019 Nothing Invented | `test/geo.js`, `test/places.js` | nothing filled with a placeholder — **285 TODO/placeholder markers** remain across `lib/`, `public/` and `test/` |
| LAW-020 Rules Belong To Kinds | `lib/entity.js`, `lib/kernel.js` | every format and validation rule owned by the kind that needs it |
| LAW-021 One Kernel | `_registry/gate.js` | every domain on the same kernel — **no domain is on the kernel yet** (`GAP-06`) |
| LAW-024 Immutable Record | `lib/security.js`, `lib/kernel.js` | one record, not three — `audit_log`, the webhook bus (`lib/events.js`) and `k_events` coexist (`GAP-27`, K08) |

---

## PART FIVE — The kernel, the domains, and the capabilities

### 5.1 The four partial kernel parts (GAP-06, P08)

| Part | Owner | What is missing |
|---|---|---|
| K05 Shape | Geo | Coordinate systems are declared and any place at any scale can be declared, but **no country, subdivision or body carries coordinates** — so "which places contain this point" answers nothing on real data (`GAP-11`). Containment scans every shape in a system with no spatial index; polygons are planar on the first two axes. |
| K08 Events | Runtime | The kernel's log is hash-chained, but `audit_log`, the webhook bus (`lib/events.js`) and `k_events` are three separate records (`GAP-27`). K08 requires one. |
| K09 Change Lifecycle | Evolution | Draft, validate, preview, approve, publish, roll back all work. The remainder: purge cannot remove codes already written in earlier event payloads, because the log is never edited. Decide and document that as the intended guarantee, or add the erasure path. |
| K12 Resolution | Context | One resolver answers what applies here and now — nearest wins, profiles order hierarchies, time windows apply, the answer says where it came from. The remainder: **rules (the Rule domain) are not yet an input** to the resolver. |

`GAP-06` says plainly that *no domain is on the kernel yet* from P09 onward. P09 (Geo), P10
(Measure/Value), P11 (Time) and P12 (Expression) have landed their domains, but the remaining domains
still read and write their own tables rather than kernel nodes. That migration is the substance of
P13–P24 and P27.

### 5.2 The 12 designed-only domains (GAP-04)

These have a contract and no code and no live route: **Constitutional Authority, Knowledge,
Observation, Evidence, Inference, Reasoning, Simulation, Causality, Possibility, Twin, Decision,
Trust.** The eight in C03 (Observation, Evidence, Inference, Reasoning, Simulation, Causality,
Possibility, Twin) are the intelligence chain. Each needs a real implementation or an explicit
recorded decision that it stays designed-only — the register says "truth" is not being told.

### 5.3 The 30 missing capabilities — 25 of 32 platform types still request them (P32, P31)

`node scripts/coverage-matrix.js` is the gate: it prints, per platform type, the capabilities
discovery still has to **request** because no capability atom provides them. Today **7 of 32 types
fully covered** (Digital goods, Education, Subscription boxes, Services and consultancy, Payments-led
super app, Mobility, Operations).

| Capability | Blocks |
|---|---|
| `delivery_slots` | **20 of 32 types** — every marketplace, grocery, quick-commerce, pharmacy, food, fashion, electronics, furniture, parts, rental, auction, group-buy, resale, dropship, made-to-order, gifts and pre-order type. The table and the engine already exist in `lib/qcommerce.js`; only the capability declaration is missing — the cheapest win on this list. |
| `size_guides` | 8 types |
| `serviceable_areas` | 4 types |
| `cold_chain` | 4 types |
| `large_item_delivery` | 5 types |
| `freshness_windows`, `sell_by_weight` | 3–4 types each |
| `supplier_direct` | 2 types |
| `fitment` | 2 types |
| `seat_maps` | event ticketing |
| `travel_itineraries` | travel, rentals and stays |
| `preorders`, `funding_goals` | pre-orders and crowdfunding |
| `kitchen_hours` | food and restaurant delivery |
| `batch_expiry`, `generic_alternatives`, `refill_reminders`, `schedule_rules` | online pharmacy and health |
| `payment_instrument_offers`, `instalments_without_cost` | national multi-category marketplace |
| `duties_at_checkout`, `customs_declarations`, `consolidated_shipping`, `gamified_rewards` | cross-border bargain marketplace |
| `club_pricing` | hypermarket and warehouse club |
| `reseller_margins`, `affiliate_commissions` | reseller and social commerce |
| `sale_events` | national marketplace |
| `dated_delivery` | gifts and flowers |
| `live_selling` | live and social video selling |

**Each one is a capability atom** with typed params, its vocabularies as rows, its life as a state
machine, its effect on a bag line as a line term where it has one, and its console and storefront
screens — per `GLOBAL_MASTER.md` §9 and §10. `lib/seed/capabilities.json` holds 90 keys today; the
catalogue needs 30 more, each backed by real code **in its own domain's files**.

**The 21 new offer and deal types** in `GLOBAL_MASTER.md` §10 are a separate slice of the same phase:
payment-instrument offers, instalments without cost, exchange offers, free gift with purchase, mix and
match, lightning deals, deal of the day and sale events, clearance, price match and lowest-price
guarantee, price-drop protection, member-only and tier prices, loyalty points, channel-only offers, happy
hours and time windows, location-based offers, clipped digital coupons, two-sided referrals, gamified
rewards, delivery-fee waivers and small-order fees.

### 5.4 The 20 planned build steps (roadmap P13–P32)

| Step | Domains | Work |
|---|---|---|
| P13 | Semantic, Context, Party, Rule, Authority | Classification, Context, Party and Rule on the kernel; **one authorisation engine** |
| P14 | Compliance | Regulations, controls, consent, subject requests, retention |
| P15 | Experience | Device types, themes, components, configured screens (`GAP-16`) |
| P16 | Communication, Notification | Channels, templates, conversations, who is told and when |
| P17 | Runtime | Workflows on today's state machines (`GAP-17`) |
| P18 | Search, Content, Guidance | Search, content, guidance; **the user manual generated** |
| P19 | Integration | The generated API, connectors, webhooks |
| P20 | Insight | Insight on today's dashboards and experiments |
| P21 | Agent | Agent on today's AI layer — bounded parties on the public API with approvals, budgets, a kill switch (DEC-007) |
| P22 | Offering, Package | Configuring by selection, blueprints, overlays, the first packages |
| P23 | Operations | Operations consolidated |
| P24 | Commerce | Business entities on the kernel; engines read the resolver; stores lose their single country and currency |
| P25 | Package, Guidance | **Launch by configuration, end to end**, for a person with the manual and for an agent (`GAP-18`) |
| P26 | Registry | More storage adapters; moving domains between databases from the console (`GAP-15`) |
| P27 | Identity, Semantic, Registry, Relationship, Context | The platform master: every kind as a row, many hierarchies, identifier schemes, inherited attributes, the maximum starter content |
| P28 | Authority, Perspective, Evolution, Package | Permissions on the master, projections and overlays; contributions reviewed and applied, added as new, or attached as an addendum |
| P29 | Package, Context, Time | Configuration by blueprint steps, each effective to the minute; discovery of mandatory, recommended, added and requested capabilities |
| P30 | Commerce, Communication, Integration, Offering | Fulfilment modes for every kind of offering; built-in media sessions beside connectors; communication on commercial terms |
| P31 | Package, Quality | The coverage matrix: every platform type launched by a test that fails while any capability is left requested |
| P32 | Commerce, Offering, Value, Rule | The missing engines and every type of deal and offer |

`GLOBAL_MASTER.md` §7 sets nine **phase gates**, each the full test suite, the registry gate, the
hard-coding audit, the white-label scan and the browser check, plus the phase's own checks. Phases 0–5
have largely landed; **phase 6 (read model for cart, checkout and orders), phase 7 (fulfilment modes,
media sessions, commercial communication), phase 8 (documentation, retired paths removed) and phase 9
(the missing engines)** remain.

### 5.5 The Universal Wallet — six remaining slices (`GLOBAL_MASTER.md` §11)

Slice 1 (definitions, wallets, an immutable balanced ledger, holds, audit evidence) is built and tested
in `test/wallet.js` — and Wallets is the one domain whose document is complete.

- [ ] **Slice 2** — conversion, FX and pricing: routes, quotes, execution (the `fx_rates` table exists; nothing uses it)
- [ ] **Slice 3** — one commission engine for seller, marketplace, affiliate, referral, reseller and provider fees, replacing three scattered implementations; settlement and payout from `lib/fin.js` onto the ledger
- [ ] **Slice 4** — rewards, gift and offer issues into wallet definitions; gift cards and vouchers (where the in-flight `lib/giftcards.js` belongs)
- [ ] **Slice 5** — interoperability, custody, asset and network: external wallet links with consent, adapters from the Provider Registry, asset identity on Value units
- [ ] **Slice 6** — compliance and jurisdiction activation: approval records per value class, operation, route and place, fail closed; issuance limits by place (UW-VAL-010 — today any registered unit may be held); risk, disputes and reconciliation cases per mismatch (UW-FIN-006 is only partial)

---

## PART SIX — The operational, data and process gaps

### 6.1 Repository hygiene and CI (the highest-leverage item in the whole list)

| Gap | What it says | The fix |
|---|---|---|
| GAP-30 | The repository sits in an iCloud-synced Desktop folder. The sync made **71 conflict copies** (`_registry/canonical 2.json`, 42 in `data/`, 26 in `test/`, the `.luxora 2.pid` pair), one hung `git add`, and its file locking may explain the intermittent test failures. **The repository belongs outside iCloud.** | Move the working tree to a non-synced path, remove the conflict copies and the zero-byte `data/*.sqlite` files. This also fixes the `disk I/O error` that stops `npm run registry` from using the default database. |
| GAP-29 | GitHub refused to start the CI jobs because the account's payments failed or its spending limit was reached. Every commit since is checked locally only. | Fix the billing or the spending limit, then run the full matrix (Node 22.13 / 22 / 24, plus the browser and Postgres jobs) on `main`. |
| GAP-23 | CI moved to the actions' Node 24 runtime (`checkout@v5`, `setup-node@v5`) on `ubuntu-24.04`; unverified until CI can run again. | Verified by the CI run above. |
| GAP-28 | Intermittent failures: the `ECONNRESET` was a 5 s keep-alive racing a reused socket (fixed, AMD-0022); the browser check's `Runtime.evaluate` timeout and a console render that misses its fixed wait under load remain unexplained. | Fix the remaining two. Move the repo out of iCloud first and re-measure — file locking is a candidate cause. |
| GAP-22 | Stripe and EasyPost have never been run against real sandboxes; deployment is a single node. | Run both against their sandboxes; then document the multi-node deployment path (the AMD-0022 keep-alive fix assumes a load balancer is already there). |

### 6.2 Truth and data

| Gap | What it says | The fix |
|---|---|---|
| GAP-04 | 12 domains with no code and no live route | Section 5.2 |
| GAP-05 | 11 laws planned, 9 partial | Part Four |
| GAP-06 | Kernel parts partial; no domain is on the kernel yet | Section 5.1 |
| GAP-07 | 375 low-confidence classification decisions await a person | Measured today in `_registry/classification.json`: **189 low-confidence containers plus 186 low-confidence concepts = 375**. Each needs a human call, then the register is re-sealed. |
| GAP-10 | The hard-coding ratchet counts 65 branches, 99 fallbacks, 8 seed-sized constants | Measured today: **51 branches, 87 fallbacks, 7 seed-sized constants** — the gap text is stale, the counts are lower. Section 6.4. |
| GAP-11 | Places carry no shapes | Kernel part K05 |
| GAP-13 | Most page text — footer columns, page headings, both consoles, emails — is still English written in code rather than catalogue keys. The storefront's copy keys already speak every catalogued language, RTL included (AMD-0023). | Move the remaining page text, both consoles and the email templates into the message catalogue. |
| GAP-15 | Custom entities exist and the platform runs on Postgres end to end (AMD-0024, `npm run check:postgres`), but there is **no per-domain storage choice and no console-driven move between databases**. | Roadmap step P26. |
| GAP-16 | Themes exist; **no device types, component registry or screen builder**. | Roadmap step P15. |
| GAP-17 | Workflow, notification, package, agent, integration and report designers described by the contracts are **not built**. | Roadmap steps P17, P19, P21, P22. |
| GAP-18 | Launch by configuration, end to end, is not yet possible. | Roadmap step P25. |
| GAP-19 | The development database holds test countries (XX, XY, Zamunda under ZA, Zephyria, Antarctica) — **awaiting the owner's go-ahead to remove**. | Needs your decision. One line of work once approved. |
| GAP-25 | Search filters by owner and category only for register entries, **not universes or corpus documents**. | Extend `lib/canonical.js` search, then LAW-013's enforcement can point at it. |
| GAP-27 | Three event records coexist | Kernel part K08 |

### 6.3 Process

| Gap | What it says | The fix |
|---|---|---|
| GAP-20 | PR #3's description does not cover its last commits. | Rewrite the PR description against the actual commits. |
| GAP-24 | `USER_MANUAL.md` is hand-written; nothing checks it against the code. | Generate it from the per-domain manual sections (Part Two) and add it to the check that already guards `docs/domains/`. |

### 6.4 The hard-coding ratchet to zero (LAW-006, GAP-10)

The ratchet stands at **51 branches, 87 fallbacks and 7 seed-sized constants**. Every one is a place
where behaviour is decided in code rather than from the registry. The ratchet may only fall —
`npm run audit:baseline` writes the lower count once it is genuinely lower.

The 7 seed-sized constants are the biggest single wins: `lib/api.js · STORE_ROUTE_SECTION` (28 lines),
`lib/authz.js · ROUTE_SECTION` (35), `lib/goip.js · GOIP_HANDLERS` (40), `lib/goip.js · INTEL` (30),
`lib/goip.js · IMPL` (47), `lib/rules.js · PROVIDERS` (20), `lib/uid.js · TABLES` (23) — 223 lines of
literal registry data that belong in `lib/seed/`, in the domain that owns each. Then the 51 branches and
87 fallbacks, largest first: `public/js/platform.js` (7 fallbacks and 107 TODO markers), `lib/goip.js`,
`lib/api.js`, `lib/mailer.js`, `lib/db.js`, `public/js/admin.js`, `public/js/app.js`.

There are also **285 TODO/FIXME/placeholder markers** across `lib/`, `public/` and `test/` — most in
`public/js/platform.js` (107), `public/js/admin.js` (55) and `public/js/app.js` (38). Under LAW-019
"nothing is filled with a placeholder", each is either a real implementation or an honest empty state.

### 6.5 The two gates that cannot run here

The white-label scan is part of every phase gate. `npm run check:browser` reports "No Chrome/Chromium
found — set CHROME_PATH" in this environment, so the browser check is unverified locally; it must run
in CI once GAP-29 is fixed.

---

## The order I would take it in

The project's own phase gates prescribe the order, and it is the right one, because the gates must stay
green between phases — and because extraction work (Part One) is only safe while the gates can prove
nothing changed.

**Phase A — make the tree honest again (a day, and it unblocks everything else).**
Fix the four failing gates (Part Three). Move the repository out of iCloud and delete the 71 conflict
copies (GAP-30). Fix GitHub billing and get CI green (GAP-29, GAP-23). Decide on the test countries
(GAP-19). Re-baseline nothing that has not genuinely improved.

**Phase B — split the domains, one at a time, starting with the money and offer spine.**
This is the largest structural block and it is what makes "nothing is mixed" true rather than aspirational.
Each extraction: routes to `lib/routes/<domain>.js`, console to `public/js/admin/<domain>.js`, tables to
the domain's own schema section, everything declared in `_registry/business-domains.json`, baseline
lowered. The ratchet proves each one.

**Phase C — the constitutional spine.**
The 10 planned laws with their checks, then the 10 partial laws' remainders. Each check is small; what
is large is choosing where each law bites. This is what makes the later phases provable rather than
assertable.

**Phase D — the kernel, then the domains on it.**
K05, K08, K09, K12. Then the 12 designed-only domains. Then the migration in P13–P24.

**Phase E — the coverage matrix.**
The 30 capability atoms and the 21 offer types, each in its own domain's files. `scripts/coverage-matrix.js`
is the gate and it already runs: 7/32 → 32/32. Route P31, P32 and `GLOBAL_MASTER.md` phase 9.

**Phase F — every domain's document and every user's manual.**
The 208 sections, the 722 route descriptions, and then `USER_MANUAL.md` generated and checked. Phase 8.

**Phase G — the operational end.**
Stripe and EasyPost against real sandboxes (GAP-22). Multi-node deployment. The remaining P26, P30 work.

**Phase H — the long tail.**
The hard-coding ratchet to zero. The 375 low-confidence classification calls. The 285 placeholder markers.

---

## What I would need from you

- **GAP-19** — go-ahead to remove the test countries (XX, XY, Zamunda, Zephyria, Antarctica) from the development database.
- **GAP-30** — approval to move the repository out of the iCloud-synced Desktop folder. It blocks CI, the browser check and possibly the intermittent failures, so it is worth doing before Phase A finishes.
- **GAP-29** — GitHub billing, which only you can fix.
- **The in-flight gift-card work** — finish and commit it as AMD-0039, or set it aside?
- **The split order** — I have put the money and offer spine first (Tier 1). If you would rather start with a different tier, that is easy to change.
- **Phase order** — the plan follows the project's own phase gates. If you would rather pull the coverage matrix forward because it is the most visible deliverable, that is defensible; it just means the kernel and law checks land after it.

Every item above is traceable to a register entry: roadmap step, gap id, law id, kernel part, coverage
row, domain-map debt, or amendment. Nothing in this list is a guess about intent — where a decision was
open I have said so rather than picked one.
