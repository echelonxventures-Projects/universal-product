# Hard-coding audit — what still names business vocabulary in code

The constitution (UCRS Ω∞, §3) allows only kernel concepts in code: Entity, Registry,
Relationship, Context, Policy, Rule, Decision, State, State Machine, Event, Authority,
Identity, Time, Evidence, Governance, Metadata. Everything else must come from a registry.
This audit measures how far the code is from that. The full generated tables are in
[`HARDCODING_AUDIT.generated.md`](HARDCODING_AUDIT.generated.md). Rebuild them with
`npm run audit:hardcoding`.

## How it was measured

`scripts/audit-hardcoding.js` boots the platform on a throwaway database. It reads the
**vocabulary the registries actually hold**: 1,405 values, covering provider ids, countries,
currencies, capability keys, platform kinds, roles and every registry-list key. It then finds
each place the code names one of those values and classifies how it is used:

| Use | Meaning | Count |
|---|---|---:|
| **branch** | logic decides on the value (`=== "paid"`, `case "percent"`, `.includes("sms")`) | **308** |
| identity | an engine names the capability it implements (`cap(t, "ride_hailing")`) | 26 |
| route | a console view key that shares a vocabulary word (`view === "sso"`) | 26 |
| fallback | a default the code falls back to (`\|\| "USD"`, `?? "order"`) | 243 |
| seed | a seed row written as code (`key: "razorpay"` inside a constant) | 728 |
| other | any other mention (labels, SQL, messages) | 4,393 |

Plus **34 seed-sized constants (2,771 lines)**, data written as JavaScript.

**Limits.** It's a heuristic. It finds only literals that equal a registry value. So it
misses copy text, brand strings and magic numbers, and it flags some word collisions (for
example, `"orders"` is both a role key and an entity name). Treat the counts as a map, not a
verdict.

## Findings, ranked by impact

### 1. State machines are written in code — 106 branches on 42 states
The status lists are registry rows (`finPayoutStatuses`, `mobilityRideStatuses`, …), but the
engines branch on literal state names: `status === "paid"`, `["pending_payment",
"cancelled"].includes(o.status)`, `if (toStatus === "dispatched")`. Adding, renaming or
re-sequencing a state means a code change in every engine that names it.
**Fix:** a state-machine registry. Each state declares its *meaning* (terminal, settled,
cancellable, billable…), and each transition declares its effects (stamp a time, release a
hold, charge a fee). Engines ask "is this state settled?" or "run this transition"; they
never name the state. *Files:* `lib/fintech.js`, `lib/mobility.js`, `lib/operations.js`,
`lib/planning.js`, `lib/trade.js`, `lib/logistics.js`, `lib/api.js`, `public/js/app.js`.

### 2. Behaviour is chosen by a vocabulary key — 162 branches on 102 values
Engines pick behaviour by naming a vocabulary entry:
- offer and promotion types: `type === "percent" || type === "flash_percent"`;
- offer scopes: `st === "brand"`;
- channels: `channel === "sms"`;
- media kinds: `kind === "video"`;
- industries in tax: `cls === "digital"`;
- AI capability dispatch: `capability === "reporting"`;
- attribution models;
- bid models.

**Fix:** each vocabulary row declares its **handler** (an offer type row says
`calc: "percent"`, a channel row says `transport: "sms"`). The kernel holds a small set of
handlers keyed by that declared name, so a new offer type that reuses a handler, or a new
channel, is one row. *Top files:* `lib/goip.js`, `lib/offers.js`, `lib/ai.js`, `lib/tax.js`,
`lib/mailer.js`, `public/js/admin.js`.

### 3. Seed data is written as JavaScript — 34 constants, 2,771 lines
The largest:

| Constant | File | Lines |
|---|---|---:|
| `ENTITY_DEFS` | `lib/entity.js` | 582 |
| `PARITY_DEFS` | `lib/entity.js` | 494 |
| `CATALOG` (capabilities) | `lib/capabilities.js` | 252 |
| `SUBDIVISIONS` | `lib/subdivisions.js` | 202 |
| `PRESETS` (blends) | `lib/capabilities.js` | 96 |
| `DEFAULTS` (brand, theme, copy, fees) | `lib/settings.js` | 90 |

Others: `REGULATIONS`, the GOIP domains and handlers, the module `MARKET`, `PROVIDER_SPECS`,
`INDUSTRIES`, `PRODUCT_TYPES`, roles. Most are already copied into registry tables on boot,
but the code keeps them as fallbacks, and some, like settings `DEFAULTS`, are read directly.
**Fix:** move each to `lib/seed/*.json`, as the applicability rules now are. Code reads the
registry and keeps no code fallback. A "first boot" step loads seeds that are missing.

### 4. Fallback defaults — 243
These are things like `|| "USD"`, `|| "order"`, `|| "email"` and default statuses on insert.
Each is a decision the platform's policy should own.
**Fix:** a defaults registry (or the existing platform policy) per concern. Code reads
`defaults.currency`, never a literal.

### 5. Engines name other engines' capabilities — 25 branches + 26 identities
An engine naming *its own* capability (`cap(tenantId, "ride_hailing")` in the ride engine) is
its identity, the same shape as a rule binding point. That's acceptable, but it's still better
expressed as a binding row. The real coupling is one engine checking **another** engine's
capability by name: `hasCap(T(s), "wallet")` inside checkout, `"aiPro"`, `"offersPro"` and
`"billingPro"` in AI, offers and billing.
**Fix:** route through binding points (`checkout.wallet` → capability), the mechanism
`lib/rules.js` now uses.

### 6. Providers named in logic — 4
`mailer.js` dispatches on `provider === "smtp"`, and notifications special-case the `"log"`
provider.
**Fix:** a provider's spec declares its transport (`transport: "smtp"`, `transport: "log"`),
and the kernel dispatches on the declared transport.

### 7. The consoles decide on vocabulary too — ~90 branches in `public/js`
Status labels and colours, offer-type forms and AI capability forms are chosen by key in the
browser.
**Fix:** the server sends each row's display metadata (label, tone, form fields) from the
registry, and the console renders what it's given.

## Progress

| Batch | What changed | Logic branches | State branches |
|---|---|---:|---:|
| Baseline | — | 308 | 106 |
| State machines, batch 1 | `lib/states.js` and 32 machines in `lib/seed/states.json`; the engines below converted | **260** | **58** |
| State machines, batch 2 (orders) | 37 machines; orders, payments, invoices, credit notes, returns and EMIs | **246** | **44** |
| State machines, batch 3 | 80 machines; tenants, compliance, fintech, GOIP, marketplace extensions, foundations, subscriptions, consoles | **207** | **6**, all word collisions, no real states |
| Declared behaviour (finding 2), server engines | vocabulary rows declare their behaviour; engines follow the row | **134** | 6 |
| Declared behaviour (finding 2), consoles | storefront, store and platform consoles read the same rows | **109** | 6 |
| Feature gates (finding 5) | engines ask binding points; catalogue rows declare policy and storefront atoms | **101** | 6 |
| Provider transports (finding 6) | provider specs declare a kernel transport; identity types declare protocols; FX sources declare `fetches` | **93** | 6 |

**Batch 1 converted these engines:**
- rides, drivers, vehicles (`lib/mobility.js`);
- purchase requests, approvals, payroll runs and lines, work orders, employees, projects, tasks (`lib/operations.js`);
- replenishment (`lib/planning.js`);
- disputes, seller payouts (`lib/fin.js`);
- quick-commerce dispatch, riders, dark stores, service areas, delivery slots (`lib/qcommerce.js`);
- RFQs, quotes, tenders, bids, supplier verification, suppliers, gold memberships, price lists (`lib/trade.js`);
- shipments (`lib/logistics.js`);
- experiments (`lib/experiments.js`);
- tickets and agents (`lib/helpdesk.js`).

`test/states.js` gates these engines: it fails if any of them compares, filters or lists one of its machine's states by name.

**Batch 2 converted:**
- orders, payments, invoices, credit notes, returns and EMIs, across `lib/api.js` (checkout, settlement, gateway webhooks and the reconcile sweep, refunds, cancellation, labels, returns, platform invoices), `lib/billing.js`, `lib/fin.js`, `lib/recurring.js`, `lib/marketplace.js` and `lib/planning.js`;
- the storefront order list, the console's order, payment and ride actions, and invoice badges. States now carry display data (label, icon, tone), and `/api/meta` serves every machine's meanings and labelled moves, so the consoles ask by tag too.

**Batch 3 converted:**
- tenants and org units (the suspended-store gate, suspend and resume);
- compliance: control verdicts, consent, and the data-subject request lifecycle, with erasure as a declared handler;
- every fintech instrument: UPI handles and collects, QR codes, payment links, mandates, escrow, split payments, KYC (the requested level names a `level:<x>` tag), bank payouts, billers, recharge plans, bill payments, recharges, BNPL accounts, EMIs, loans, insurance and gift vouchers;
- GOIP: settlements, entitlements, budgets, redemptions, offers, and offer governance, whose verbs are the machine's `actions`;
- marketplace extensions: onboarding, seller offers, inbound shipments, buyer claims (resolutions by `resolution:<side>` tags) and smart fulfilment;
- UCOS foundation lifecycles;
- Subscribe & Save schedules and cycles (allowed actions are `can:<action>` tags the storefront reads), memberships, platform plan subscriptions, modules, promotions and contracts;
- webhook deliveries;
- the remaining console buttons (drivers, payroll, work orders, onboarding, invoices, settlements, org units).

**Finding 2, server engines — vocabulary rows now declare behaviour:**

| Vocabulary | What a row declares |
|---|---|
| AI capabilities | the engine that runs it and how its billable units are counted |
| AI report sections | the implementation that renders it |
| Tax classes | a fixed rate or the rule field that supplies it, the tax modes where a valid buyer VAT number reverse-charges it, the default class |
| Offer types | pro-gated, cart-wide, currency-bound, percentage, risky when uncapped, ranking weight |
| Offer channels and scopes | whether a channel includes promotions and gates pro types; how a scope matches items |
| Stacking policies and coupon kinds | what a policy blocks; a new-customers-only kind |
| Bid models | the ad event it charges on, the unit it is priced per, its ranking basis |
| Delivery channels | its providers and transports, the address it reaches and its pattern, its environment adapter |
| Sign-in types | which ones enrol a shared secret |
| Risk decisions | the score threshold, the effect, whether a blocklist hit forces it |
| Sort orders and ad event kinds | the columns or flags a sort uses; which events a shopper may report |
| Shipping classes and product types | a surcharge setting; whether the type is a service |
| Membership benefits | the checkout effect they grant |
| GOIP objectives, attribution models, touchpoints, party types, asset classes, audiences, funders | the ranker, the attribution implementation, the touchpoint that carries value, uncredited parties, money classes, always-on audiences and their win-back offers, the merchant's own funder |

Existing installs pick the new fields up through `registry.addFields()`, which never overwrites an operator's value, and `registry.upgradeShape()`, which turns plain-name lists into rows. `test/behaviour.js` edits rows to show the engines follow them, and fails if a converted engine compares against one of those keys.

**Finding 2, consoles:**
- The storefront reads each product type's `purchase` mode and `plain` flag, each media kind's `player`, the default shipping class, the `contextGroups` registry for checkout contexts, and a membership tier's price.
- The store console takes vehicle kinds and capacities from the registry, marks storefront feature toggles by the catalogue's `settings_atom`, reads the AI tier from a `premium` flag, renders each AI capability's form from its row's `params`, and writes an offer scope's value into the field its row declares.
- The platform console draws FX rate sources from a `fxSources` registry (the sync accepts a source that `fetches`), offers funders from funding rows marked `selectable`, and badges touchpoints that carry value.

**What remains in the 66 registry hits is not business vocabulary:**
- page routes and UI action names (`home`, `product`, `gift`, `track`);
- dashboard widget renderers (`bar`, `line`);
- form field keys (`media`, `title`);
- the kernel effect names that rows now declare (`block`, `hold`, `free_shipping`);
- the guest owner-id prefix;
- the currency entity's delete guard;
- the identity field shown on its own (`sku`).

**Finding 3 — seed data is now data:**
- 31 constants, about 3,100 lines, moved out of JavaScript into `lib/seed/<module>.json`, one file per module: capabilities, settings, subdivisions, entity, compliance, parity registries, GOIP, modules, providers, tax, offers, meta, authz and themes.
- Each module now reads `const NAME = SEED_<MODULE>.NAME`. Comments that lived inside a literal are kept above that line.
- The ten seed-sized constants that remain (355 lines) are kernel tables: implementation and handler tables, route wiring and the UID table list. Two are deliberate exceptions: `ucos.js` `DOCS`, which holds functions, and `db.js` `CATEGORY_SEED`, which belongs to the boot module.
- `test/seeds.js` parses every seed file. It fails if a business literal of 20 or more lines reappears in `lib/` outside the declared kernel tables.

**Finding 4 — defaults are data (fallbacks: 210 → 96):**
- `lib/defaults.js` resolves a value the caller did not give:
  - `currency(tenantId)` returns the store's chosen currency, else its country's, else the currency of the platform's default country;
  - `of(list)` returns the row a registry flags `default`.
- `lib/seed/defaults.json` declares the default row for 23 lists. Boot flags that row once, after every seeder has run, and never moves an operator's own flag. `/api/meta` serves the defaults to the consoles.
- About 60 hard-coded `"USD"` values now resolve through `currency()`: wallet, fintech, trade, billing, GOIP, module invoices and AI usage. The hard-coded list of currency codes in `lib/offers.js` now asks the currency master.
- About 80 vocabulary fallbacks now resolve through `of()`: offer channels, staff roles, product types, dashboard types, GOIP domains, objectives, distribution, calendars and funders, sort orders, attribution models, incoterms, B2B document kinds and tiers, UoM, fintech circles and biller categories, and privacy request kinds. GOIP's own `defaultOf` now delegates to `of()`.
- The ride and driver forms read vehicle kinds from `mobilityVehicleKinds` instead of a list in the prompt text.
- **Bug fixed:** the store currency lookups read a `tenants.currency` column that does not exist. `billing.tenantCurrency` and `global.getTenantCurrency` would have thrown instead of returning a currency, and `global.setTenantCurrency` would have failed instead of saving it. They now use the store's commerce setting.
- `test/defaults.js` shows that moving a list's flag, or changing a store's currency, changes what the engines fall back to. It fails if a literal fallback to a declared default or a currency code returns.
- **What the 96 remaining hits are:**
  - placeholder names (`"Untitled"`, `"General"`, `"Customer"`) and CSS values (`"block"`);
  - kernel words: a ledger function's own entry kind, the GOIP benefit handlers' units, the user roles, and graph edge names;
  - the widget endpoint's own distribution;
  - the demo and boot seeders;
  - the affiliate module's tier, which has no registry;
  - column defaults in the database schema.

**Finding 5 — engines ask binding points, not each other's capabilities (branches: 109 → 101):**
- **Feature gates:** the `featureGates` registry (`lib/seed/gates.json`, `lib/gates.js`) maps each binding point to the capability that opens it, its source (module or catalogue), an optional module setting and the refusal message.
- **Points now gated:**
  - `checkout.wallet`: the checkout balance, the wallet API, the module-release guard and the storefront gift page;
  - `checkout.logistics_guard`, `checkout.tax_per_line` and `checkout.login_required` (the providing module's setting);
  - `identity.hardening`, applied on install;
  - `seo.tools`, `reco.engine`, `listing.tools` and `billing.self_pay`;
  - `ai.premium`, `offers.pro` and `storefront.currency_switch`.
- **Moving a feature to another module is a row edit.** `/api/config`, `/api/session` and the store's module list serve every point's state, so the storefront and the store console ask points too.
- **Capability catalogue rows now declare:**
  - `settings_atom`, which replaces the `STOREFRONT_KEYS` code list;
  - `seed_enabled`, which replaces `SEED_ENABLED`;
  - the platform `policy` flag that must allow the feature, with its refusal. This replaces three code paths that named `coupons` and `fiscalSelection`.
- `test/gates.js` shows that installing a module opens its points and that repointing a gate closes it. It fails if an engine or console checks a module capability by name.
- **Identity, which stays:** an engine naming the capability it *is*, such as the ride engine's `ride_hailing` or GOIP checking its own module, and console panels for that same capability.

**Finding 6 — engines dispatch on a provider's declared transport (branches: 101 → 93):**
- **Notification providers:** a provider's spec (`provider_defs.spec`) either describes an HTTP request for the spec engine or declares a kernel `transport`. The seed declares `notification:smtp` → `smtp` and `notification:log` → `log`, and boot writes those declarations into `provider_defs`.
- `lib/mailer.js` holds the kernel transports (`KERNEL`): `smtp`, which speaks SMTP directly and reads a platform default from the URL its `urlEnv` names, and `log`, which is `local` and writes to the server log. Delivery dispatches on `kernelOf(provider)` and never compares a provider's name. The provider row on file decides; the seed only stands in when there is no row.
- **What was converted:**
  - the mailer's send path and its platform defaults (`LX_SMTP_URL`, and `LX_SMS_PROVIDER`, which is now any provider the SMS channel lists);
  - the store notifier in `lib/api.js`: a local provider logs, a kernel transport sends through the kernel, and anything else goes through the spec engine;
  - provisioning: a new store starts with the first notification provider whose transport is local, not a literal `notify:log`.
- **Identity provider types declare their `protocols`** (`sso` → saml, oidc; `oauth`, `openid` and `ldap` → oidc). The external flow runs the type's first protocol unless the provider's config picks another protocol the type declares. A new type that names a protocol the engine does not speak is refused. The field reaches operator-edited lists through `addFields`.
- **FX sources:** the feed setting looks up the chosen `fxSources` row, and a row that `fetches` needs an http(s) URL. This replaces the `"feed"`/`"manual"` literals.
- `test/transports.js` (13 checks) shows that a provider added as a row and declaring a transport is followed, that removing a declaration takes effect, and that protocols follow the type row. It fails if an engine compares against a notification provider, FX source or identity type by name. The `password` flow is exempt because it is the engine's own kernel flow.
- **What stays:** `const KIND = "notification"` in the mailer (counted as one fallback, so 96 → 97) is the provider kind the mailer serves, which is identity. Boot still re-asserts every seeded spec, as it did before, so an operator's edit to a seeded provider's spec does not survive a restart.

**New registry entries now reach existing installs on every boot.** A new machine, binding or vocabulary row is appended additively, with no stamp bump needed. `test/states.js` covers this.



**Status vocabularies are finished:** no engine branches on a status name. The six remaining audit hits are word collisions: the outbound mode `offline`, the UGC entity `review`, and the WebAuthn attestation format `packed`. The remaining work is the audit's other findings (2 to 7).

## What step 1 removed (applicability rules)

- **Vocabularies are now seed data in `lib/seed/rules.json`:** subject types, dimensions,
  services, segments, channels, banks, bank identifiers, country groups and payment methods.
  `lib/rules.js` names none of them. A test enforces this.
- **Engines name only their binding point.** There are 32 `ruleBindings` rows. Each says what
  the point decides, the facts it sets (its service) and, for a guarded entry point, its
  checks and which input fields feed which facts. Re-pointing one is a data edit, and a test
  proves it with the payout bank check.
- **Rule overrides map to fields through each subject type's `params` row**, not a code map.
- **Where a fact comes from is declared per dimension:** the platform's row (`column`), a
  lookup (`derive`), the request (`header`, `default`), a binding, or a computed provider.
- **Generic sources replace every special case.** `list:`, `rows:` (with filters), `values:`
  (JSON columns), `entity:` and `+` unions replace the named sources for methods, capabilities,
  modules, sign-in methods, kinds, platforms, currencies and segments. Sign-in types are now a
  registry list.
- **The staff exemption is the binding's `exemptRoles`.** The AI fallback is the free plan's
  provider and its first registered model and currency.

**Still in code in the rules area (kernel or relationships, listed for completeness):**
- the provider × country availability check, which reads the context's country;
- house shipping recognised by an id prefix in provisioning;
- the names of the match operators (`in`, `any`, `prefix`, `group`) and of the one computed
  provider (`segments`).

## Proposed order of work

1. **State-machine registry** (finding 1). It's the largest source of logic branching and
   touches money paths, so it needs the most tests.
2. **Declared handlers for vocabularies** (finding 2), starting with offers/GOIP and AI
   dispatch.
3. **Seeds out of code** (finding 3), largest first. `ENTITY_DEFS` and `PARITY_DEFS` alone are
   1,076 lines.
4. **Defaults registry** (finding 4), and **cross-engine bindings** (finding 5).
5. **Provider transports** (finding 6) and **console metadata** (finding 7).
6. **A gate test** that runs this audit and fails when a new branch on a registry value
   appears, so the count only goes down.
