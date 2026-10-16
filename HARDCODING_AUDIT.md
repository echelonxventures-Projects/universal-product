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

**Next state batch:** orders and payments (`lib/api.js`; the `order` machine already exists), compliance, GOIP, fintech instruments, and the consoles (`public/js`).

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
